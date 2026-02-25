function buscar() {
  const input = document.getElementById("searchInput").value.trim();
  if (input === "") return;

  const seccio = document.querySelector(".noticies");

  // Eliminem marques anteriors
  const marks = seccio.querySelectorAll("mark");
  marks.forEach(mark => {
    mark.replaceWith(mark.textContent);
  });

  const regex = new RegExp(input, "gi");

  function destacar(node) {
    if (node.nodeType === 3) { // node de text
      const text = node.nodeValue;
      if (regex.test(text)) {
        const span = document.createElement("span");
        span.innerHTML = text.replace(regex, match => `<mark>${match}</mark>`);
        node.replaceWith(span);
      }
    } else if (node.nodeType === 1 && node.childNodes) {
      node.childNodes.forEach(destacar);
    }
  }

  destacar(seccio);
}
