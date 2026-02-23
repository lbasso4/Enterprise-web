const calendar = document.getElementById("calendar");
const monthTitle = document.getElementById("monthTitle");

let today = new Date();
let currentMonth = today.getMonth();
let currentYear = today.getFullYear();

const months = [
  "Gener","Febrer","Març","Abril","Maig","Juny",
  "Juliol","Agost","Setembre","Octubre","Novembre","Desembre"
];

const weekdays = ["Dl","Dt","Dc","Dj","Dv","Ds","Dg"];

function renderCalendar() {
  calendar.innerHTML = "";
  monthTitle.textContent = months[currentMonth] + " " + currentYear;

  // Dibuixar dies de la setmana
  weekdays.forEach(day => {
    calendar.innerHTML += `<div class="weekday">${day}</div>`;
  });

  let firstDay = new Date(currentYear, currentMonth, 1).getDay();
  firstDay = (firstDay === 0) ? 6 : firstDay - 1;

  let daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

  // Espais abans del dia 1
  for (let i = 0; i < firstDay; i++) {
    calendar.innerHTML += "<div></div>";
  }

  // Dibuixar dies del mes
  for (let day = 1; day <= daysInMonth; day++) {
    let className = "day";

    if (
      day === today.getDate() &&
      currentMonth === today.getMonth() &&
      currentYear === today.getFullYear()
    ) {
      className += " today";
    }

    calendar.innerHTML += `<div class="${className}">${day}</div>`;
  }
}

function changeMonth(direction) {
  currentMonth += direction;

  if (currentMonth > 11) {
    currentMonth = 0;
    currentYear++;
  }

  if (currentMonth < 0) {
    currentMonth = 11;
    currentYear--;
  }

  renderCalendar();
}

renderCalendar();
