const API = "http://176.123.166.80:5000";

async function loadPrinters() {
    const res = await fetch(API + "/printers");
    const data = await res.json();

    const container = document.getElementById("printers");
    container.innerHTML = "";

    data.forEach(p => {
        const div = document.createElement("div");
        div.className = "card";

        let html = `<b>${p.name}</b><br>`;

        p.carts.forEach(c => {
            html += `
            ${c.name} (${c.qty})
            <button class="btn plus" onclick="update(${c.id}, '+')">+</button>
            <button class="btn minus" onclick="update(${c.id}, '-')">-</button>
            <br>
            `;
        });

        div.innerHTML = html;
        container.appendChild(div);
    });
}

async function update(id, act) {
    await fetch(API + "/update", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({id, act})
    });

    loadPrinters();
}

loadPrinters();
