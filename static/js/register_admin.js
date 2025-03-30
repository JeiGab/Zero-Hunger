document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("registroForm").addEventListener("submit", function (event) {
        event.preventDefault(); 

        let formData = new FormData(this);

        fetch("{{ url_for('registro_admin') }}", {
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
                document.getElementById("registroForm").reset();
            }
            });
        })
        .catch(error => console.error("Error:", error));
    });
});