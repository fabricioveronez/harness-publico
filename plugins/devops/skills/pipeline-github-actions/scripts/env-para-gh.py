#!/usr/bin/env python3
"""Grava as chaves de um .env como secrets/variables do GitHub Actions sem imprimir valores.

Classifica cada chave pelo uso nos workflows:
  - `secrets.NOME` no YAML  -> secret
  - `vars.NOME` no YAML     -> variable
  - não referenciada        -> ignorada (a menos que --todos, aí vira secret)

Aceita: comentários, `export `, aspas simples/duplas, valores multilinha entre aspas
e blocos PEM (-----BEGIN ...----- até -----END ...-----) sem aspas.

Padrão é dry-run (só lista nomes, destino e escopo). Use --aplicar para gravar.

Escopo: secrets vão para o repositório, salvo `--env-secret NOME=ambiente`, que grava
no environment (crie-o antes: gh api -X PUT repos/dono/repo/environments/<ambiente>).

--fingerprint NOME deriva a chave pública e as fingerprints (MD5 e SHA256) de uma chave
privada do .env sem imprimi-la nem deixá-la em disco depois (arquivo 0600 em diretório
temporário privado, apagado na hora — ssh-keygen não lê chave privada de stdin).

Uso:
  env-para-gh.py .env -R dono/repo [--workflows .github/workflows] [--aplicar]
                 [--secret NOME ...] [--var NOME ...] [--env-secret NOME=ambiente ...] [--todos]
  env-para-gh.py .env --fingerprint SSH_PRIVATE_KEY
"""
import argparse
import pathlib
import re
import os
import subprocess
import sys
import tempfile

CHAVE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$")


def parse_env(texto):
    linhas = texto.splitlines()
    resultado = {}
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        i += 1
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        m = CHAVE.match(linha)
        if not m:
            raise ValueError(f"linha {i}: formato não reconhecido (conteúdo omitido)")
        nome, resto = m.group(1), m.group(2).strip()

        if resto[:1] in ("'", '"'):
            aspa = resto[0]
            corpo = resto[1:]
            partes = []
            while True:
                fim = corpo.find(aspa)
                if fim != -1:
                    partes.append(corpo[:fim])
                    break
                partes.append(corpo)
                if i >= len(linhas):
                    raise ValueError(f"{nome}: aspas sem fechamento")
                corpo = linhas[i]
                i += 1
            valor = "\n".join(partes)
            if aspa == '"':
                valor = valor.replace("\\n", "\n")
        elif resto.startswith("-----BEGIN"):
            partes = [resto]
            while not partes[-1].strip().startswith("-----END"):
                if i >= len(linhas):
                    raise ValueError(f"{nome}: bloco PEM sem -----END")
                partes.append(linhas[i].strip())
                i += 1
            valor = "\n".join(partes)
        else:
            valor = re.sub(r"\s+#.*$", "", resto)

        if "-----BEGIN" in valor and not valor.endswith("\n"):
            valor += "\n"  # ssh/openssl exigem newline final na chave
        resultado[nome] = valor
    return resultado


def uso_nos_workflows(pasta):
    secrets, variables = set(), set()
    p = pathlib.Path(pasta)
    if not p.is_dir():
        return secrets, variables
    for arq in list(p.glob("*.yml")) + list(p.glob("*.yaml")):
        texto = arq.read_text(encoding="utf-8")
        secrets |= set(re.findall(r"secrets\.([A-Za-z0-9_]+)", texto))
        variables |= set(re.findall(r"vars\.([A-Za-z0-9_]+)", texto))
    secrets.discard("GITHUB_TOKEN")
    return secrets, variables


def fingerprint(valor):
    with tempfile.TemporaryDirectory() as d:
        os.chmod(d, 0o700)
        caminho = os.path.join(d, "k")
        fd = os.open(caminho, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(valor)
        r = subprocess.run(["ssh-keygen", "-y", "-P", "", "-f", caminho], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("não foi possível derivar a chave pública: a chave tem passphrase ou o formato está quebrado")
    pub = r.stdout.strip()
    print("pública:", pub)
    for alg in ("md5", "sha256"):
        fp = subprocess.run(["ssh-keygen", "-l", "-E", alg, "-f", "-"], input=pub + "\n", capture_output=True, text=True)
        print(f"{alg}:", fp.stdout.split()[1] if fp.returncode == 0 else "erro")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("env")
    ap.add_argument("-R", "--repo")
    ap.add_argument("--workflows", default=".github/workflows")
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--secret", action="append", default=[], help="forçar NOME como secret")
    ap.add_argument("--var", action="append", default=[], help="forçar NOME como variable")
    ap.add_argument("--env-secret", action="append", default=[], metavar="NOME=AMBIENTE",
                    help="gravar o secret NOME no environment AMBIENTE")
    ap.add_argument("--todos", action="store_true", help="chaves não referenciadas viram secret")
    ap.add_argument("--fingerprint", metavar="NOME", help="só mostra pública/fingerprints da chave NOME")
    a = ap.parse_args()

    try:
        env = parse_env(pathlib.Path(a.env).read_text(encoding="utf-8"))
    except ValueError as e:
        sys.exit(f"erro ao ler {a.env}: {e}")

    if a.fingerprint:
        if a.fingerprint not in env:
            sys.exit(f"{a.fingerprint} não existe em {a.env}")
        fingerprint(env[a.fingerprint])
        return
    if not a.repo:
        sys.exit("faltou -R dono/repo")
    ambientes = {}
    for item in a.env_secret:
        nome, _, amb = item.partition("=")
        if not amb:
            sys.exit(f"--env-secret espera NOME=ambiente, recebeu {item}")
        ambientes[nome] = amb

    usados_s, usados_v = uso_nos_workflows(a.workflows)
    plano = []
    for nome, valor in env.items():
        if nome in a.var:
            destino = "variable"
        elif nome in a.secret:
            destino = "secret"
        elif nome in usados_v:
            destino = "variable"
        elif nome in usados_s:
            destino = "secret"
        elif a.todos:
            destino = "secret"
        else:
            destino = "ignorada"
        obs = []
        if "\n" in valor.rstrip("\n"):
            obs.append("multilinha")
        if not valor:
            obs.append("VAZIA")
        if destino == "secret" and nome in ambientes:
            escopo = f"env:{ambientes[nome]}"
        elif destino == "ignorada":
            escopo = "-"
        else:
            escopo = "repo"
        plano.append((nome, destino, escopo, ", ".join(obs)))

    largura = max([len(p[0]) for p in plano] + [4])
    print(f"{'NOME'.ljust(largura)}  DESTINO   ESCOPO         OBS")
    for nome, destino, escopo, obs in plano:
        print(f"{nome.ljust(largura)}  {destino.ljust(8)}  {escopo.ljust(13)}  {obs}")

    faltando = sorted((usados_s | usados_v) - set(env))
    if faltando:
        print("\nReferenciadas nos workflows mas ausentes no .env (gravar por outro caminho):")
        for n in faltando:
            print(f"  - {n} ({'variable' if n in usados_v else 'secret'})")

    if not a.aplicar:
        print("\n(dry-run — nada foi gravado; rode com --aplicar)")
        return

    falhas = 0
    for nome, destino, escopo, obs in plano:
        if destino == "ignorada":
            continue
        if "VAZIA" in obs:
            print(f"pulando {nome}: valor vazio")
            continue
        valor = env[nome]
        if destino == "secret":
            cmd = ["gh", "secret", "set", nome, "-R", a.repo]
            if escopo.startswith("env:"):
                cmd += ["--env", escopo[4:]]
            r = subprocess.run(cmd, input=valor, text=True, capture_output=True)
        else:
            cmd = ["gh", "variable", "set", nome, "-R", a.repo, "--body", valor]
            r = subprocess.run(cmd, text=True, capture_output=True)
        if r.returncode == 0:
            print(f"ok    {destino:8}  {escopo:13}  {nome}")
        else:
            falhas += 1
            # stderr do gh não contém o valor
            print(f"FALHA {destino:8}  {nome}: {r.stderr.strip()}")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
