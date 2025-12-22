const API = "/static" === window.location.pathname.substring(0,7) ? "" : "http://127.0.0.1:5000";

// 1. Contadores y Resumen
function cargarInventario() {
    fetch(`${API}/inventario/resumen`)
        .then(res => res.json())
        .then(data => {
            const disp = data.disponible || 0;
            const pres = data.prestado || 0;
            document.getElementById("disponible").textContent = disp;
            document.getElementById("prestado").textContent = pres;
            if(document.getElementById("total")) {
                document.getElementById("total").textContent = disp + pres;
            }
        });
}

// 2. Tabla de GESTIÓN (Aquí agregamos Editar/Eliminar)
function cargarItemsInventario() {
    fetch(`${API}/inventario/items`)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("tabla-items");
            if (!tbody) return; 
            tbody.innerHTML = "";

            data.forEach(item => {
                const row = document.createElement("tr");
                row.className = "hover:bg-slate-50 transition-colors border-b";

                const badgeColor = item.estado === 'disponible' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700';

                row.innerHTML = `
                    <td class="px-6 py-4">
                        <div class="font-mono text-sm font-bold text-slate-800">${item.uid}</div>
                        <div class="text-[10px] text-slate-400 uppercase tracking-tight">UID RFID</div>
                    </td>
                    <td class="px-6 py-4">
                        <div class="text-sm font-semibold text-slate-700">${item.nombre}</div>
                        <div class="text-xs text-slate-400">${item.categoria}</div>
                    </td>
                    <td class="px-6 py-4">
                        <div class="text-[11px] text-slate-500 italic max-w-[200px] truncate" title="${item.especificaciones}">
                            ${item.especificaciones || 'Sin detalles'}
                        </div>
                    </td>
                    <td class="px-6 py-4 text-center">
                        <span class="px-3 py-1 rounded-full text-[10px] font-black uppercase ${badgeColor}">
                            ${item.estado}
                        </span>
                    </td>
                    <td class="px-6 py-4 text-right flex justify-end gap-3">
                        <button onclick="prepararEdicion('${item.uid}', '${item.nombre}', '${item.especificaciones}')" class="text-blue-500 hover:text-blue-700 transition">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button onclick="eliminarItem('${item.uid}')" class="text-red-400 hover:text-red-600 transition">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(err => console.error("Error al cargar inventario:", err));
}
// 3. FUNCIONES DE ACCIÓN
function eliminarItem(uid) {
    Swal.fire({
        title: '¿Estás seguro?',
        text: `Vas a eliminar el ítem ${uid}. Esta acción no se puede deshacer.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`${API}/items/${uid}`, { method: 'DELETE' })
                .then(res => res.json())
                .then(data => {
                    Swal.fire('¡Eliminado!', 'El ítem ha sido borrado.', 'success');
                    cargarItemsInventario();
                    cargarInventario();
                });
        }
    });
}

// Lógica para el Modal de Edición
function prepararEdicion(uid, nombre, especificaciones, estado) {
    document.getElementById("edit-uid").value = uid;
    // El campo de categoría ahora lo usamos para mostrar el nombre del producto
    document.getElementById("edit-categoria").value = nombre; 
    document.getElementById("edit-referencia").value = especificaciones;
    
    // Asegúrate de tener un campo para el estado en tu modal HTML
    if(document.getElementById("edit-estado")) {
        document.getElementById("edit-estado").value = estado;
    }
    
    document.getElementById("modalEditar").classList.remove("hidden");
}

function cerrarModal() {
    document.getElementById("modalEditar").classList.add("hidden");
}

function guardarCambios() {
    const uid = document.getElementById("edit-uid").value;
    const categoria = document.getElementById("edit-categoria").value;
    const referencia = document.getElementById("edit-referencia").value;

    fetch(`${API}/items/${uid}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ categoria, id_referencia: referencia })
    })
    .then(res => res.json())
    .then(data => {
        // Ejemplo de SweetAlert2 en lugar de alert()
        Swal.fire({
            icon: 'success',
            title: 'Actualizado',
            text: 'Los datos del cable han sido modificados con éxito',
            timer: 2000,
            showConfirmButton: false
        });
        cerrarModal();
        cargarItemsInventario();
        cargarInventario();
    });
}

// 4. Historial rápido (Últimos 5)
function cargarMovimientos() {
    fetch(`${API}/movimientos`)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("tabla-movimientos");
            if(!tbody) return;
            tbody.innerHTML = "";
            data.slice(0, 5).forEach(mov => {
                const row = document.createElement("tr");
                const badgeColor = mov.accion === 'entrada' ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700';
                row.innerHTML = `
                    <td class="px-6 py-4 font-mono text-xs font-bold">${mov.uid}</td>
                    <td class="px-6 py-4 text-center">
                        <span class="px-2 py-0.5 rounded-full text-[9px] font-black uppercase ${badgeColor}">
                            ${mov.accion}
                        </span>
                    </td>
                    <td class="px-6 py-4 text-[11px] text-slate-400 italic">${mov.fecha}</td>
                `;
                tbody.appendChild(row);
            });
        });
}

// Inicialización
cargarInventario();
cargarItemsInventario();
cargarMovimientos();

setInterval(() => {
    cargarInventario();
    cargarMovimientos();
    cargarItemsInventario();
}, 10000); // 10 segundos para no saturar