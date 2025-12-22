const botonBuscar = document.getElementById("buscar");
const tabla = document.getElementById("tabla-movimientos");

botonBuscar.addEventListener("click", () => {
    const uid = document.getElementById("uid").value;
    const accion = document.getElementById("accion").value;

    // 1. Usa la dirección local de tu Flask
    const API_BASE = "http://127.0.0.1:5000/movimientos";

    // 2. Construir los parámetros
    let params = new URLSearchParams();
    if (uid) params.append("uid", uid);
    if (accion) params.append("accion", accion);

    const urlFinal = params.toString() ? `${API_BASE}?${params.toString()}` : API_BASE;

    console.log("Buscando en:", urlFinal); // Para que veas en la consola si se arma bien

    fetch(urlFinal)
        .then(response => {
            if (!response.ok) throw new Error("Error en la respuesta del servidor");
            return response.json();
        })
        .then(data => {
            tabla.innerHTML = "";
            data.forEach(mov => {
                const fila = document.createElement("tr");
                fila.innerHTML = `
                    <td class="px-6 py-4">${mov.uid}</td>
                    <td class="px-6 py-4">${mov.accion}</td>
                    <td class="px-6 py-4">${mov.fecha}</td>
                `;
                tabla.appendChild(fila);
            });
        })
        .catch(error => console.error("Error:", error));
});