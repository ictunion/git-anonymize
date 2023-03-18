{ python3
, stdenv
, nix-gitignore
, makeWrapper
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
    nativeBuildInputs = [ makeWrapper ];
    propagatedBuildInputs = [ pythonEnv ];
    dontBuild = true;
    installPhase = ''
      mkdir -p $out/bin
      cp $src/git-anonymize.py $out/bin/git-anonymize
      wrapProgram "$out/bin/git-anonymize" --suffix PYTHONPATH : "${pythonEnv}"
    '';
  }
