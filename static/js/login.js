document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Evita la recarga de la página

    let formData = new FormData(this);

    fetch("/login", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        Swal.fire({
            icon: data.success ? "success" : "error",
            title: data.success ? "Inicio de sesión exitoso" : "Error",
            text: data.message
        }).then(() => {
            if (data.success) {
                window.location.href = data.redirect; // Redirige al usuario
            }
        });
    })
    .catch(error => {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: "Hubo un problema al procesar la solicitud."
        });
        console.error("Error:", error);
    });
});
