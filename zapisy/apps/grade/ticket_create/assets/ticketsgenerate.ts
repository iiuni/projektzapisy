import * as bigInt from 'big-integer';
import { sha256 } from 'js-sha256';
import { get as getCookie } from "js-cookie";
import axios from "axios";


const axiosInstance = axios.create({
    baseURL: '/grade/ticket/',
    headers: {
        'X-CSRFToken': getCookie('csrftoken'),
    },
});

type PollDataDict = { [pollId: number]: PollData };

class PublicKey {
    n: bigInt.BigInteger;
    e: bigInt.BigInteger;

    constructor(n: string, e: string) {
        this.n = bigInt(n);
        this.e = bigInt(e);
    }

    blind(m: bigInt.BigInteger, r: bigInt.BigInteger): bigInt.BigInteger {
        return m.times(r.modPow(this.e, this.n)).mod(this.n);
    }

    unblind(m: bigInt.BigInteger, r: bigInt.BigInteger): bigInt.BigInteger {
        return m.times(r.modInv(this.n)).mod(this.n);
    }
}

class PollData {
    pubKey: PublicKey;
    name: string;
    type: string;
    id: number;
    ticket?: Ticket;

    constructor(pubkey: PublicKey, name: string, type: string, id: number) {
        this.pubKey = pubkey;
        this.name = name;
        this.type = type;
        this.id = id;
    }

    getSigningRequest(ticket: Ticket): SigningRequest {
        let ticketToSign = this.pubKey.blind(hash(ticket.m), ticket.r);

        return {
            ticket: ticketToSign.toString(),
            id: this.id
        };
    }
}

interface Ticket {
    m: bigInt.BigInteger;
    r: bigInt.BigInteger;
}

interface TicketForUser {
    name: string;
    type: string;
    id: number;
    ticket: string
    signature: string;
}

interface SigningRequest {
    ticket: string;
    id: number;
}

function hash(m: bigInt.BigInteger): bigInt.BigInteger {
    return bigInt(sha256(m.toString()), 16);
}

/** This function is needed, since big-integer module doesn't support secure random numbers generation.
 *  Source: https://github.com/peterolson/BigInteger.js/pull/108
*/
function secureRandBetween(min: bigInt.BigInteger, max: bigInt.BigInteger): bigInt.BigInteger {
    var range = max.subtract(min);
    while(true) {
        var rand = random(range.bitLength().toJSNumber());
        if(range.geq(rand)) {
            return min.add(rand);
        }
    }
    function random(bits: number): bigInt.BigInteger {
        let bytes = Math.ceil(bits / 8);
        let randomArray = window.crypto.getRandomValues(new Uint8Array(bytes));
        let bigIntRandomArray: bigInt.BigInteger[] = new Array();
        for (let num of randomArray) {
            bigIntRandomArray.push(bigInt(num));
        }
        let randBigNum = bigInt.fromArray(bigIntRandomArray, 256);
        return randBigNum;
    }
}

function generateRandomTicket(pubKey: PublicKey): Ticket {
    const randMin: bigInt.BigInteger = bigInt(2);
    const randMax: bigInt.BigInteger = pubKey.n;

    let m: bigInt.BigInteger;
    let r: bigInt.BigInteger;
    // while condition will probably never happen, but we will check it just to be safe
    do {
        m = secureRandBetween(randMin, randMax);
        r = secureRandBetween(randMin, randMax);
    } while (bigInt.gcd(r, pubKey.n) === bigInt.one);

    return { m: m, r: r };
}

async function getPollDataFromServer(): Promise<PollDataDict> {
    let pollDataDict: PollDataDict = {};

    let polls = await axiosInstance.post('/get-poll-data');
    for (let poll of polls.data) {
        let pubKey = new PublicKey(poll.key.n, poll.key.e);
        let pollData = new PollData(pubKey, poll.poll_info.name, poll.poll_info.type, poll.poll_info.id);

        pollDataDict[poll.poll_info.id] = pollData;
    }

    return pollDataDict;
}

async function getSignedTicketsFromServer(pollDataDict: PollDataDict) {
    let signingRequests = {
        signing_requests: new Array(),
    }

    for (let id in pollDataDict) {
        let pollData = pollDataDict[id];
        let ticket = generateRandomTicket(pollData.pubKey);
        pollData.ticket = ticket;
        let signingRequest = pollData.getSigningRequest(ticket);

        signingRequests.signing_requests.push(signingRequest)
    }

    let signedTickets = await axiosInstance.post('/sign-tickets', signingRequests);
    return signedTickets;
}

export default async function generateTicketsMain(): Promise<string> {
    let pollDataDict = await getPollDataFromServer();
    let signedTickets = await getSignedTicketsFromServer(pollDataDict);

    let ticketsForUser: { [tickets: string]: TicketForUser[] } = {
        tickets: new Array(),
    };

    for (let signedTicket of signedTickets.data) {
        let pollData = pollDataDict[signedTicket.id];
        let blindedSignature = bigInt(signedTicket.signature);
        let ticket = pollData.ticket!;
        let unblindedSignature = pollData.pubKey.unblind(blindedSignature, ticket.r);
        let ticketForUser: TicketForUser = {
            name: pollData.name,
            type: pollData.type,
            id: pollData.id,
            ticket: ticket.m.toString(),
            signature: unblindedSignature.toString(),
        };

        ticketsForUser.tickets.push(ticketForUser);
    }

    return JSON.stringify(ticketsForUser, null, 2);
}