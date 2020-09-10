// Displays a EU-required Cookie information bar at the bottom of the screen
// unless the user had already dismissed it.
import "cookieconsent";
import "cookieconsent/build/cookieconsent.min.css";

window.addEventListener("load", function () {
  (window as any).cookieconsent.initialise({
    palette: {
      popup: {
        background: "#222222",
      },
      button: {
        background: "#00709e",
      },
    },
    showLink: false,
    theme: "classic",
    position: "bottom",
    content: {
      message:
        "System zapisów wykorzystuje pliki cookies. Korzystanie" +
        " z witryny oznacza zgodę na ich zapis lub odczyt według" +
        " ustawień przeglądarki.",
      dismiss: "OK",
    },
  });
});
