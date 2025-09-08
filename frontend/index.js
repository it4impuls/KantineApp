const API_URL = "http://kantinekasse.impulsreha.local:8000";


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

// --------- DOM helpers-------------------
function setVisibility(elementId, visible) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = visible ? "flex" : "none";

        // if we show a popup, disable re-focussing UserID input
        toggleFocus(!visible);
    }
}

function focusUserID() {
    document.getElementById("userID").focus()
}

function toggleFocus(enabled) {
    if (enabled) {
        document.addEventListener("click", focusUserID);
    } else {
        document.removeEventListener("click", focusUserID);
    }
}

// abomination to get a set cookie (required for csrf))
function getCookie(name) {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}

function setCookie(cname, cvalue, exhrs) {
    const d = new Date();
    d.setTime(d.getTime() + (exhrs * 60 * 60 * 1000));
    let expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

// fetch with crsf and session
function do_fetch(addr, method, body) {
    return fetch(`${API_URL}/${addr}/`, {
        method: method,
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: method == "POST" ? body : undefined,
        signal: AbortSignal.timeout(5000),
        // credentials: "POST" ? "include" : undefined

    })
}

async function submit_form(event) {
    const e_userID = document.getElementById("userID");
    const e_menus = document.getElementsByClassName("menulabel")
    const loader = document.getElementById("popup-loader")
    event.preventDefault();

    var formdata = new FormData(event.target);
    if (!formdata.get("userID")) {
        alert("keine ID-Nummer");
        return;
    } else if (!formdata.get("ordered_item")) {
        alert("kein Menü");
        return;
    } else if (!formdata.get("tax")) {
        alert("keine Steuer");
        return;
    }
    e_userID.value = "";

    for (let element of e_menus) {
        // depends on the input being the only element!
        // to be safe we could use:
        // element.querySelector('input[type="radio"]:checked').checked=false
        // but thats way less readable and I dont think we will ever add more children.

        if (element.firstElementChild.checked) {
            element.firstElementChild.checked = false
            break;
        }
    }

    try {

        setVisibility("popup-loader", true)
        var orderResponse = await do_fetch("orders", "POST", formdata).finally(() => { setVisibility("popup-loader", false) });
    } catch (error) {
        var msg = error.message;
        if (error instanceof TypeError) {
            msg = "Request konnte nicht gesendet werden. Ist das Gerät mit dem internet verbunden?"
        } else if (error instanceof DOMException) {
            msg = "Verbindung mit dem server konnte nicht aufgebaut werden! (Timeout)."
        } else {
            msg = "unknown error: " + msg
        }
        alert(msg);
        console.log(error);
        return;
    }
    var orderText = await orderResponse.text();
    var response_obj = JSON.parse(orderText);
    if (orderResponse.status == 403) {    // unauthenticated
        setVisibility("popup-login", true);
        return
    }
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
                    API_URL + response_obj["order"]["url"],
                    {
                        method: "PUT",
                        headers: {
                            "X-CSRFToken": getCookie("csrftoken")
                        },
                        body: formdata,
                        credentials: "include",
                    }
                );
                if (!put_response.ok) {
                    alert(await put_response.text());
                }
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



// build menu, check auth-tokens
window.addEventListener("load", async (event) => {
    document.getElementById("form").addEventListener("submit", submit_form);
    document.getElementById("login-form").addEventListener("submit", login);

    // check auth token, see Authentication functions
    if (check_authenticated().then(() => {
        // Hide the loader, show content
        setVisibility("popup-loader", false);
    })) {
        setVisibility("popup-login", false);
    } else {
        setVisibility("popup-login", true);
    }




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




// -------------------Authentication functions-----------------------------------------------------------
// https://dev.to/wiljeder/secure-authentication-with-jwts-rotating-refresh-tokens-typescript-express-vanilla-js-4f41

async function login(e) {
    e.preventDefault();
    const formdata = new FormData(e.currentTarget)
    try {
        // getCSRF()
        const res = await do_fetch("auth/login", "POST", formdata)

        if (!res.ok) {
            console.log("error while logging in")
            console.log(res)
            alert(await res.text())
            return;
        }
        console.log("Logged in!");
        setVisibility("popup-login", false);
    } catch (error) {
        console.error("Login failed:", error);
        console.log("Login error occurred!");
    }
}

async function getCSRF() {
    try {
        let res = await fetch(`${API_URL}/csrf/`, {
            method: "GET",
            signal: AbortSignal.timeout(5000)
        });

        if (res.ok) {
            console.log(res)
            const crsf = await res.body["csrfToken"]

            setCookie("csrftoken", crsf, 200)
            return crsf
        } else {
            console.log("error retrieving crsf: " + await res.body())
            return
        }
        console.log("is logged in")
    } catch (error) {
        console.error("Error retrieving crsf:", error);
        alert(error.text)
        return false
    }
    return true
}

async function check_authenticated(options) {
    try {
        getCSRF()
        let res = await do_fetch("auth/verify", "GET", {});

        // If the token has expired or is invalid, try refreshing
        if (!res.ok) {
            setVisibility("popup-login", true);
            return false
        }
        console.log("is logged in")
    } catch (error) {
        console.error("Error in check_authenticated:", error);
        console.log("Error occurred while fetching secret.");
        alert(error.text)
        return false
    }
    return true
}