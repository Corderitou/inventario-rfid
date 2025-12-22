const API = ""; // Flask servirá esto desde la misma ruta

// 1. Cargar el catálogo al abrir la página
document.addEventListener("DOMContentLoaded", () => {
    fetch('/catalogo')
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById("codigo_referencia");
            select.innerHTML = '<option value="">-- Selecciona un producto --</option>';
            
            data.forEach(item => {
                const option = document.createElement("option");
                option.value = item.codigo; // Ej: CAB-001
                option.textContent = `${item.codigo} - ${item.nombre} (${item.categoria})`;
                select.appendChild(option);
            });
        })
        .catch(err => console.error("Error cargando catálogo:", err));
});

// 2. Función para guardar el nuevo ítem
async function guardarItem() {
    const uidInput = document.getElementById("uid");
    const codRefInput = document.getElementById("codigo_referencia");

    const uid = uidInput.value.trim();
    const codigo_referencia = codRefInput.value;

    if (!uid || !codigo_referencia) {
        return Swal.fire("Error", "Debes completar todos los campos", "error");
    }

    try {
        const res = await fetch('/items', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                uid: uid, 
                codigo_referencia: codigo_referencia 
            })
        });

        const data = await res.json();

        if (res.ok) {
            Swal.fire("¡Éxito!", "Ítem vinculado al catálogo correctamente", "success")
                .then(() => {
                    document.getElementById("uid").value = ""; // Limpiar para el siguiente
                });
        } else {
            Swal.fire("Error", data.error, "error");
        }
    } catch (err) {
        Swal.fire("Error", "No se pudo conectar con el servidor", "error");
    }
}