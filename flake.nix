{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils = {
      url = "github:numtide/flake-utils";
    };
  };

  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
        dependencies = [
          (pkgs.python310.withPackages
            (ps: with ps; [
              openai-whisper
              pyaudio
              playsound
              pyautogui
              dbus-python
              # pydbus
              plyer
              termcolor
              (
                buildPythonPackage
                  rec {
                    pname = "beepy";
                    version = "1.0.7";
                    src = fetchPypi {
                      inherit pname version;
                      sha256 = "sha256-gXNI/zzAmKyo0d57wVKSt2L94g/MCgIPzOp5NpQNW18=";
                    };
                    doCheck = false;
                    propagatedBuildInputs = [
                      ps.simpleaudio
                    ];
                  }
              )
            ]))
        ];
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [ dependencies ];
        };

        defaultPackage = pkgs.stdenv.mkDerivation {
          name = "defaultPackage";
          buildInputs = dependencies;
          src = ./.;
          dontBuild = true;
          installPhase = ''
            mkdir -p $out/bin
            cp -r . $out
            # add a `whisper-input` script, which just calls `python3 whisper-input.py`
            touch $out/bin/whisper-input
            echo "#!${pkgs.stdenv.shell}" > $out/bin/whisper-input
            echo "python3 $out/whisper-input.py" >> $out/bin/whisper-input
            chmod +x $out/bin/whisper-input
          '';
        };
      }
    );
}






