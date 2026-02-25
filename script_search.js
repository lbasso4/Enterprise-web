function buscar() {
  let input = document.getElementById("searchInput").value;

  if (input.trim() === "") {
    alert("Escriu alguna paraula per cercar.");
  } else {
    alert("Has cercat: " + input);
  }
}
