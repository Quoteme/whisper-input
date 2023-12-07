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
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs;  [
            (python310.withPackages
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
        };
      }
    );
}
