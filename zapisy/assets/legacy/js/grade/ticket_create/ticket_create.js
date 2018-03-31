/*
 required: Big Integers
 http://www.leemon.com/crypto/BigInt.html
 */

if (typeof Ticket != 'undefined') {
} else {
    var Ticket = new Object();
}
Ticket.create = Object();
Ticket.create.init = function () {
    $("#progressbar").progressbar({ value:0 });
    Ticket.create.t_array = new Array();
    Ticket.create.m_array = new Array();
    Ticket.create.unblindst_array = new Array();
    Ticket.create.unblindt_array = new Array();
    Ticket.create.k_array = new Array();
    Ticket.create.RAND_BITS = 512;
    Ticket.create.used = false;

    $("#connection_choice_button").click(function (event) {
        event.preventDefault();
        if (Ticket.create.used) {
            return false;
        }
        Ticket.create.used = true;

        Ticket.create.step1();
    })
}

// Request public keys from the server
Ticket.create.step1 = function () {
    dataString = $("#connection_choice").serialize()
    $("#progressbar").progressbar("option", "value", 10);
    $.ajax({
        type:"POST",
        url:"/grade/ticket/ajax_tickets1",
        dataType:'json',
        data:dataString,
        success:Ticket.create.step2
    });
    return false;
}

// Once we have the public keys, use them to generate
// tickets, then send them to the server for signing
Ticket.create.step2 = function (keys) {
    $("#progressbar").progressbar("option", "value", 30);
    console.warn("I received public keys from the server:", keys);
    $.each(keys, Ticket.create.t_generator);
    var hidden = document.createElement('input')
    hidden.name = 'ts'
    hidden.type = 'hidden'
    hidden.value = JSON.stringify(Ticket.create.t_array)
    console.warn("Will ask Python to sign those tickets:", hidden.value);
    $("#connection_choice").append(hidden);
    dataString = $("#connection_choice").serialize()
    $.ajax({
        type:"POST",
        url:"/grade/ticket/ajax_tickets2",
        dataType:'json',
        data:dataString,
        success:Ticket.create.step3
    });
}

// The server signed our generated tickets and sent
// them to us; previously we'd shuffle them with some modular
// arithmetic, but this is now disabled as that algorithm
// it not compatible with pycryptodome anymore and it provided
// no extra security one way or another
// Now this function essentially just resends the server's response
// back to it so it can render the tickets in tickets_save.html
Ticket.create.step3 = function (unblinds) {
    $("#progressbar").progressbar("option", "value", 70);
    $.each(unblinds, Ticket.create.unblinds_generator);

    var hidden = document.createElement('input')
    hidden.name = 'unblindst'
    hidden.type = 'hidden'
    hidden.value = JSON.stringify(Ticket.create.unblindst_array)
    $("#connection_choice").append(hidden);
    var hidden = document.createElement('input')
    hidden.name = 'unblindt'
    hidden.type = 'hidden'
    hidden.value = JSON.stringify(Ticket.create.unblindt_array)
    $("#connection_choice").append(hidden);
    $("#progressbar").progressbar("option", "value", 100);
    $('#connection_choice').submit();
}

Ticket.create.unblinds_generator = function (index, unblind) {
    if (unblind[1] == "Nie jesteś przypisany do tej ankiety") {
        Ticket.create.unblindst_array.push(unblind[1])
        Ticket.create.unblindt_array.push(bigInt2str(Ticket.create.m_array[index], 10))
    }
    else if (unblind[1] == "Bilet już pobrano") {
        Ticket.create.unblindst_array.push(unblind[1])
        Ticket.create.unblindt_array.push(bigInt2str(Ticket.create.m_array[index], 10))
    }
    else {
        var ticket = unblind[0];
        var ticketSignature = unblind[1][0];
        Ticket.create.unblindt_array.push(ticket);
        Ticket.create.unblindst_array.push(ticketSignature);

        // FIXME disabled this after we transition to Python3/pycryptodome
        // the legacy signing/verification algo used by pycrypto
        // that allowed this to work is no longer supported

        //var st = str2bigInt(unblind[1][0], 10, 10)
        // var n = str2bigInt(unblind[1][1], 10, 10)
        // var e = str2bigInt(unblind[1][2], 10, 10)
        // var rk = inverseMod(Ticket.create.k_array[index], n)
        // Ticket.create.unblindst_array.push(bigInt2str(multMod(mod(st, n), mod(rk, n), n), 10))
        // Ticket.create.unblindt_array.push(bigInt2str(Ticket.create.m_array[index], 10))
    }
}

Ticket.create.t_generator = function (key, val) {
    var m = randBigInt(512, 0)
    console.warn("t_generator:", val); 
    $.each(val, function (nr, g) {
        var n = str2bigInt(g[0], 10, 10)
        var e = str2bigInt(g[1], 10, 10)
        var bits = bitSize(n)

        do
        {
            var k = randBigInt(bits, 0)
        } while ((greater(k, n) || greater(int2bigInt(2, 2, 1), k)) && !equalsInt(GCD(k, n), 1)) ;

        Ticket.create.k_array.push(k);
        Ticket.create.m_array.push(mod(m, n));
        var a = mod(m, n)
        var b = powMod(k, e, n)
        var t = multMod(a, b, n)

        Ticket.create.t_array.push(bigInt2str(t, 10))
    });

}

$(Ticket.create.init)
