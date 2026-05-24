/** Autenticação e CRUD de pets no painel admin */
const TOKEN_KEY = "adocao_admin_token";
const ADMIN_KEY = "adocao_admin_user";

const STATUS_LABELS = {
  available: "Disponível",
  pending: "Em processo",
  adopted: "Adotado",
};

const SPECIES_LABELS = {
  gato: "Gato",
  cao: "Cão",
};

let editingPetHasPhoto = false;

function getToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}

function setSession(token, admin) {
  sessionStorage.setItem(TOKEN_KEY, token);
  sessionStorage.setItem(ADMIN_KEY, JSON.stringify(admin));
}

function clearSession() {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(ADMIN_KEY);
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = "/admin";
    return false;
  }
  return true;
}

async function api(path, options = {}) {
  const headers = options.headers || {};
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const response = await fetch(path, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const msg = data.error || data.message || data.msg || "Erro na requisição";
    throw new Error(msg);
  }
  return data;
}

async function handleLogin(event) {
  event.preventDefault();
  const errorEl = document.getElementById("loginError");
  errorEl.hidden = true;

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  try {
    const data = await api("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    setSession(data.token, data.admin);
    window.location.href = "/admin/painel";
  } catch (err) {
    errorEl.textContent = err.message || "E-mail ou senha inválidos.";
    errorEl.hidden = false;
  }
}

function initAdminPanel() {
  if (!requireAuth()) return;

  const admin = JSON.parse(sessionStorage.getItem(ADMIN_KEY) || "{}");
  document.getElementById("adminEmail").textContent = admin.email || "";

  document.getElementById("logoutBtn").addEventListener("click", () => {
    clearSession();
    window.location.href = "/admin";
  });

  document.getElementById("petForm").addEventListener("submit", savePet);
  document.getElementById("cancelEdit").addEventListener("click", resetForm);
  document.getElementById("photo").required = true;

  loadPets();
}

async function loadPets() {
  const loading = document.getElementById("listLoading");
  const wrap = document.getElementById("petsTableWrap");
  const body = document.getElementById("petsTableBody");

  try {
    const data = await api("/api/pets?limit=100");
    loading.hidden = true;
    wrap.hidden = false;
    body.innerHTML = "";

    if (!data.pets || data.pets.length === 0) {
      body.innerHTML = '<tr><td colspan="6">Nenhum pet cadastrado.</td></tr>';
      return;
    }

    data.pets.forEach((pet) => {
      const tr = document.createElement("tr");
      const photo = pet.photo_url
        ? `<div class="photo-thumb"><img src="${pet.photo_url}" alt=""></div>`
        : '<div class="photo-empty" aria-hidden="true">—</div>';
      const contact = pet.owner_contact
        ? escapeHtml(pet.owner_contact)
        : '<span class="text-muted">—</span>';
      tr.innerHTML = `
          <td class="cell-photo">${photo}</td>
          <td><strong>${escapeHtml(pet.name)}</strong></td>
          <td>${SPECIES_LABELS[pet.species] || pet.species}</td>
          <td>${contact}</td>
          <td>${STATUS_LABELS[pet.status] || pet.status}</td>
          <td>
            <div class="table-actions">
              <button type="button" data-edit="${pet.id}">Editar</button>
              <button type="button" class="btn-danger" data-delete="${pet.id}">Excluir</button>
            </div>
          </td>`;
      body.appendChild(tr);
    });

    body.querySelectorAll("[data-edit]").forEach((btn) => {
      btn.addEventListener("click", () => startEdit(btn.dataset.edit, data.pets));
    });
    body.querySelectorAll("[data-delete]").forEach((btn) => {
      btn.addEventListener("click", () => deletePet(btn.dataset.delete));
    });
  } catch (err) {
    loading.textContent = err.message;
    if (err.message.includes("401") || err.message.includes("Token")) {
      clearSession();
      window.location.href = "/admin";
    }
  }
}

function startEdit(id, pets) {
  const pet = pets.find((p) => p.id === id);
  if (!pet) return;

  document.getElementById("formTitle").textContent = "Editar pet";
  document.getElementById("petId").value = pet.id;
  document.getElementById("species").value = pet.species || "gato";
  document.getElementById("name").value = pet.name || "";
  document.getElementById("breed").value = pet.breed || "";
  document.getElementById("age_years").value = pet.age_years ?? "";
  document.getElementById("temperament").value = pet.temperament || "";
  document.getElementById("description").value = pet.description || "";
  document.getElementById("owner_contact").value = pet.owner_contact || "";
  document.getElementById("status").value = pet.status || "available";
  document.getElementById("is_vaccinated").checked = !!pet.is_vaccinated;
  document.getElementById("is_neutered").checked = !!pet.is_neutered;
  document.getElementById("cancelEdit").hidden = false;
  document.getElementById("photo").value = "";
  editingPetHasPhoto = !!pet.photo_url;
  document.getElementById("photo").required = !editingPetHasPhoto;
  document.getElementById("photoHint").textContent = editingPetHasPhoto
    ? "Deixe em branco para manter a foto atual."
    : "Obrigatória — selecione uma imagem.";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetForm() {
  document.getElementById("formTitle").textContent = "Novo pet";
  document.getElementById("petForm").reset();
  document.getElementById("petId").value = "";
  document.getElementById("species").value = "gato";
  document.getElementById("cancelEdit").hidden = true;
  editingPetHasPhoto = false;
  document.getElementById("photo").required = true;
  document.getElementById("photoHint").textContent = "Obrigatória ao cadastrar um novo pet.";
  hideMessages();
}

function hideMessages() {
  document.getElementById("formError").hidden = true;
  document.getElementById("formSuccess").hidden = true;
}

function buildFormData() {
  const fd = new FormData();
  fd.append("species", document.getElementById("species").value);
  fd.append("name", document.getElementById("name").value.trim());
  fd.append("breed", document.getElementById("breed").value.trim());
  const age = document.getElementById("age_years").value;
  if (age !== "") fd.append("age_years", age);
  fd.append("temperament", document.getElementById("temperament").value.trim());
  fd.append("description", document.getElementById("description").value.trim());
  fd.append("owner_contact", document.getElementById("owner_contact").value.trim());
  fd.append("status", document.getElementById("status").value);
  fd.append("is_vaccinated", document.getElementById("is_vaccinated").checked ? "true" : "false");
  fd.append("is_neutered", document.getElementById("is_neutered").checked ? "true" : "false");
  const photo = document.getElementById("photo").files[0];
  if (photo) fd.append("photo", photo);
  return fd;
}

async function savePet(event) {
  event.preventDefault();
  hideMessages();
  const errorEl = document.getElementById("formError");
  const successEl = document.getElementById("formSuccess");
  const petId = document.getElementById("petId").value;
  const ownerContact = document.getElementById("owner_contact").value.trim();
  const photo = document.getElementById("photo").files[0];

  if (!ownerContact) {
    errorEl.textContent = "Contato do responsável é obrigatório.";
    errorEl.hidden = false;
    return;
  }
  if (!photo && !petId) {
    errorEl.textContent = "Foto do pet é obrigatória.";
    errorEl.hidden = false;
    return;
  }
  if (petId && !photo && !editingPetHasPhoto) {
    errorEl.textContent = "Foto do pet é obrigatória.";
    errorEl.hidden = false;
    return;
  }

  const fd = buildFormData();

  try {
    if (petId) {
      await api(`/api/pets/${petId}`, { method: "PUT", body: fd });
      successEl.textContent = "Pet atualizado com sucesso!";
    } else {
      await api("/api/pets", { method: "POST", body: fd });
      successEl.textContent = "Pet cadastrado com sucesso!";
    }
    successEl.hidden = false;
    resetForm();
    loadPets();
  } catch (err) {
    errorEl.textContent = err.message;
    errorEl.hidden = false;
  }
}

async function deletePet(id) {
  if (!confirm("Excluir este pet permanentemente?")) return;
  try {
    await api(`/api/pets/${id}`, { method: "DELETE" });
    loadPets();
  } catch (err) {
    alert(err.message);
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
