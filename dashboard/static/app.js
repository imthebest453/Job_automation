const toggle = document.getElementById("theme-toggle");


const currentTheme = localStorage.getItem("theme");


if(currentTheme === "dark"){

    document.body.classList.add("dark");

    toggle.innerHTML="☀️";

}



toggle.addEventListener("click",()=>{


document.body.classList.toggle("dark");



let darkMode = document.body.classList.contains("dark");



if(darkMode){

    localStorage.setItem("theme","dark");

    toggle.innerHTML="☀️";

}

else{

    localStorage.setItem("theme","light");

    toggle.innerHTML="🌙";

}


});