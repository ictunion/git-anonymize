{ python3
, stdenv
, nix-gitignore
}:
let
  pythonEnv =
    python3.withPackages(ps: [
      ps.git-filter-repo
      ps.tomli
    ]);
in
  stdenv.mkDerivation {
    pname = "git-anonymize";
    version = "0.1.0";
    src = nix-gitignore.gitignoreSource [] ./.;
    propagatedBuildInputs = [ pythonEnv ];
    dontBuild = true;
    installPhase = ''
      mkdir -p $out/bin
      ln -s $src/git-anonymize.py $out/bin/git-anonymize
    '';
  }

