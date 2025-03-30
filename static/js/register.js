document.getElementById("register-form").addEventListener("submit", function(event) {
    event.preventDefault();  // Evita la recarga de la página

    let formData = new FormData(this);

    fetch("/register", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        Swal.fire({
            icon: data.success ? "success" : "error",
            title: data.success ? "Registro exitoso" : "Error al registrarse",
            text: data.message
        }).then(() => {
            if (data.success) {
                window.location.href = "/login";
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
