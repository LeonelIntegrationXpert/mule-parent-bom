# deploy_poms.py
import argparse, subprocess, sys, os, shutil
from datetime import datetime

def resolve_maven(root, mvn_path_cli=None):
    # 1) Prioriza wrapper na raiz
    for name in ("mvnw.cmd", "mvnw"):
        p = os.path.join(root, name)
        if os.path.isfile(p):
            return p
    # 2) --mvn-path explícito
    if mvn_path_cli:
        if os.path.isfile(mvn_path_cli):
            return mvn_path_cli
        raise SystemExit(f"Maven não encontrado em --mvn-path: {mvn_path_cli}")
    # 3) PATH
    for name in ("mvn.cmd", "mvn"):
        found = shutil.which(name)
        if found:
            return found
    # 4) Variáveis de ambiente
    for env in ("MAVEN_HOME", "M3_HOME"):
        base = os.getenv(env)
        if base:
            for exe in ("mvn.cmd", "mvn"):
                cand = os.path.join(base, "bin", exe)
                if os.path.isfile(cand):
                    return cand
    raise SystemExit(
        "Maven não encontrado.\n"
        "- Opções:\n"
        "  a) Adicione Maven ao PATH (mvn/mvn.cmd)\n"
        "  b) Use o Wrapper (mvnw/mvnw.cmd na raiz)\n"
        "  c) Passe --mvn-path C:\\caminho\\para\\mvn.cmd"
    )

def run(cmd, cwd, log_path, title):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    print(f"\n====== {title} ======")
    with open(log_path, "w", encoding="utf-8", errors="ignore") as lf:
        rc = subprocess.call(cmd, cwd=cwd, stdout=lf, stderr=subprocess.STDOUT, text=True)
    with open(log_path, "r", encoding="utf-8", errors="ignore") as lf:
        tail = "".join(lf.readlines()[-120:])
    print(tail)
    if rc != 0:
        raise SystemExit(f"[ERRO] Veja o log: {log_path}")

def main():
    parser = argparse.ArgumentParser(description="Clean, Install e Deploy de BOM e Parent POM no Anypoint Exchange")
    parser.add_argument("--client-id",     default=os.getenv("ANYPOINT_CLIENT_ID", "083d83056c5b4c08b2cfa523ce811c4c"))
    parser.add_argument("--client-secret", default=os.getenv("ANYPOINT_CLIENT_SECRET", "6e0D7191660746da958e6a50A11438F7"))
    parser.add_argument("--mvn-path", help="Caminho do mvn/mvn.cmd (ex.: C:/apache-maven/bin/mvn.cmd)")
    parser.add_argument("--no-skip-tests", action="store_true", help="Não pular testes (por padrão os testes são pulados)")
    args = parser.parse_args()

    root        = os.path.abspath(os.path.dirname(__file__))
    settings    = os.path.join(root, ".maven", "settings.xml")
    bom_pom     = os.path.join(root, "bom", "pom.xml")     # <- usando common-bom (como no seu layout)
    parent_pom  = os.path.join(root, "parent-pom", "pom.xml")
    logs        = os.path.join(root, "logs")
    mvn         = resolve_maven(root, args.mvn_path)

    # sanity check
    for path, label in [(settings,".maven/settings.xml"), (bom_pom,"common-bom/pom.xml"), (parent_pom,"parent-pom/pom.xml")]:
        if not os.path.isfile(path):
            raise SystemExit(f"Arquivo não encontrado: {label} -> {path}")

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    common = [
        mvn, "-U", "-B",
        "-s", settings,
        f"-Dclient.id={args.client_id}",
        f"-Dclient.secret={args.client_secret}",
    ]
    if not args.no_skip_tests:
        common += ["-DskipTests", "-DskipITs", "-DskipMunitTests"]

    print("============================================================")
    print("Deploy de POMs para Anypoint Exchange (ordem correta)")
    print(f"Raiz:     {root}")
    print(f"Maven:    {mvn}")
    print(f"Settings: {settings}")
    print(f"Logs:     {logs}")
    print("============================================================")

    # ---------- BOM ----------
    # (opcional) baixar dependências/plugins do BOM
    run(common + ["-f", bom_pom, "dependency:go-offline"], root, os.path.join(logs, f"go-offline-bom-{ts}.log"), "[PREP] Go-offline BOM")

    # 1) BOM: clean install
    run(common + ["-f", bom_pom, "clean", "install"], root, os.path.join(logs, f"install-bom-{ts}.log"), "[1/4] BOM: clean install")

    # 2) BOM: deploy (para o distributionManagement do BOM)
    run(common + ["-f", bom_pom, "deploy"], root, os.path.join(logs, f"deploy-bom-{ts}.log"), "[2/4] BOM: deploy")

    # ---------- Parent ----------
    # (agora que o BOM está instalado, o parent já resolve local)
    run(common + ["-f", parent_pom, "dependency:go-offline"], root, os.path.join(logs, f"go-offline-parent-{ts}.log"), "[PREP] Go-offline Parent")

    # 3) Parent: clean install
    run(common + ["-f", parent_pom, "clean", "install"], root, os.path.join(logs, f"install-parent-{ts}.log"), "[3/4] Parent: clean install")

    # 4) Parent: deploy
    run(common + ["-f", parent_pom, "deploy"], root, os.path.join(logs, f"deploy-parent-{ts}.log"), "[4/4] Parent: deploy")

    print("\n====== Concluído com sucesso. ======")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
