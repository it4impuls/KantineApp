const url = "http://kantinekasse.impulsreha.local:8000";


function showCustomConfirm(message) {
    return new Promise((resolve) => {
        const popup = document.getElementById("popup-query");
        const msg = document.getElementById("popup-message");
        const yesBtn = document.getElementById("popup-yes");
        const noBtn = document.getElementById("popup-no");

        msg.textContent = message;
        popup.style.display = "flex";

        const cleanup = () => {
            popup.style.display = "none";
            yesBtn.removeEventListener("click", onYes);
            noBtn.removeEventListener("click", onNo);
        };

        const onYes = () => {
            cleanup();
            resolve(true);
        };

        const onNo = () => {
            cleanup();
            resolve(false);
        };

        yesBtn.addEventListener("click", onYes);
        noBtn.addEventListener("click", onNo);
    });
}

async function submit_form(event){
    const e_userID = document.getElementById("userID");
    const e_menus = document.getElementsByClassName("menulabel")
    const loader =document.getElementById("popup-loader")
    event.preventDefault();

    var formadata = new FormData(event.target);
    if (!formadata.get("userID")) {
        alert("keine ID-Nummer");
        return;
    } else if (!formadata.get("ordered_item")) {
        alert("kein Menü");
        return;
    } else if (!formadata.get("tax")) {
        alert("keine Steuer");
        return;
    }
    e_userID.value = "";

    for (let element of e_menus){
        // depends on the input being the only element!
        // to be safe we could use:
        // element.querySelector('input[type="radio"]:checked').checked=false
        // but thats way less readable and I dont think we will ever add more children.
        
        if(element.firstElementChild.checked){
            element.firstElementChild.checked=false
            break;
        }
    }

    try {
        
        loader.style.display = "flex";
        var orderResponse = await fetch(url + "/orders/", {
            method: "POST",
            body: formadata,
            signal: AbortSignal.timeout(2000)
    
        }).finally(()=>{loader.style.display = "none";});
    } catch (error) {
        var msg = error.message;
        if (error instanceof TypeError) {
            msg = "Request konnte nicht gesendet werden. Ist das Gerät mit dem internet verbunden?"
        } else if (error instanceof DOMException) {
            msg = "Verbindung mit dem server konnte nicht aufgebaut werden! (Timeout)."
        } 
        alert(msg);
        console.log(error);
        
        return;
    }
    var orderText = await orderResponse.text();
    var response_obj = JSON.parse(orderText);
    if (orderResponse.status >= 400) {
        if (
            Object.hasOwn(response_obj, "userID") &&
            Object.hasOwn(response_obj, "order")
        ) {
            if (
                await showCustomConfirm(
                    "Der Benutzer hat heute schon bestellt: " +
                        response_obj["order"]["ordered_item"] +
                        "€ + " +
                        response_obj["order"]["tax"] +
                        "% Steuer. Soll die Bestellung mit den neuen Daten korrigiert werden?"
                )
            ) {
                var put_response = await fetch(
                    url + response_obj["order"]["url"],
                    { method: "PUT", body: formadata }
                );
                /*if (put_response.status == 200) {
                    alert("Erfolgreich");
                } else {
                    alert(await put_response.text());
                }*/
            }
        } else if (response_obj["userID"]) {
            alert(response_obj["userID"]);
        } else {
            alert(orderText);
        }
    } /*else {
        alert("Erfolgreich");
    }*/
};



window.addEventListener("load", (event) => {
    document.getElementById("form")
        .addEventListener("submit", submit_form);

    document.addEventListener("click", () => {
        document.getElementById("userID").focus();
    });
    

    preise = [
        "3.00",
        "3.50",
        "4.50",
        "6.00",
        "6.50",
        "6.90",
        "7.00",
        "7.50",
        "7.90",
        "8.50",
    ];

    form = document.getElementById("menus");
    preise.forEach((preis) => {
        label = document.createElement("label");
        input = document.createElement("input");
        input.name = "ordered_item";
        input.id = "menu_" + preis;
        input.value = preis;
        input.type = "radio";
        input.classList.add("input_invis");
        input.required = true;

        label.innerHTML = preis + "€";
        label.name = "menulabel";
        label.classList.add("menulabel");
        label.classList.add("btn");

        form.appendChild(label);
        label.appendChild(input);
    });
});