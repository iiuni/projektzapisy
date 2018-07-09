class CreateTickets {
    constructor() {
        this.tickets = []; // t_array
        this.coupons = []; // m_array
        this.blindingFactors = []; // k_array
        this.unblindst = []; // unblindst_array
        this.unblindt = []; // unblindt_array
        this.randBits = 512;
        this.used = false;
        this.progressBar = document.getElementById("progress-bar");
        this.button = document.getElementById("connections-choice-button");
    }

    init() {
        if (this.button != null) {
            this.button.onclick = (event) => {
                event.preventDefault();
                if (!this.used) {
                    this.used = true;
                    this.getKeys()
                        .then(keys => {
                                keys.forEach(key => this.generateTicket(key));
                                this.setProgressBar(30);
                                return JSON.stringify(this.tickets);
                            }
                        ).then(tickets => {
                        let formData = $("#get-tickets-form").serialize();
                        let csrftoken = formData.split("csrfmiddlewaretoken=")[1];
                        let form = new FormData();
                        form.append('ts', JSON.stringify(this.tickets));
                        return fetch("/grade/ticket/ajax_tickets2", {
                            method: 'POST',
                            headers: {
                                'Accept': 'application/json',
                                // 'Content-Type': 'application/x-www-form-urlencoded',
                                'X-Requested-With': 'XMLHttpRequest',
                                'X-CSRFToken': csrftoken
                            },
                            credentials: "same-origin",
                            body: form
                        }).then(response => {
                            if (response.ok) {
                                return response.json();
                            } else {
                                return []
                            }
                        }).then(signedTickets => {
                            console.log(signedTickets);
                        });
                    });
                }
            }
        }
    }

    getKeys() {
        this.setProgressBar(10);
        let formData = $("#get-tickets-form").serialize();
        let csrftoken = formData.split("csrfmiddlewaretoken=")[1];
        return fetch("/grade/ticket/ajax_tickets1", {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken
            },
            credentials: "same-origin"
        }).then(response => {
            if (response.ok) {
                return response.json();
            } else {
                return [];
            }
        });
    }

    finished() {
        this.setProgressBar(100);
        this.used = false;
    }

    generateTicket(value) {
        const m = randBigInt(this.randBits, 0);
        let n = str2bigInt(value[0][0], 10, 10);
        let e = str2bigInt(value[0][1], 10, 10);
        let bits = bitSize(n);
        let k = 0;
        do {
            k = randBigInt(bits, 0);
        } while ((greater(k, n) || greater(int2bigInt(2, 2, 1), k)) && !equalsInt(GCD(k, n), 1));
        this.blindingFactors.push(k);
        let a = mod(m, n);
        this.coupons.push(a);
        let b = powMod(k, e, n);

        this.tickets.push(bigInt2str(multMod(a, b, n), 10));
    }

    setProgressBar(value) {
        if (this.progressBar != null) {
            this.progressBar.style.width = value + "%";
        }
    }
}

$(() => {
    new CreateTickets().init();
});
