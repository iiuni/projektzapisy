// These models correspond to their respective counterparts implemented in
// Django. The data being transferred from the Django application to the Vue
// components is quite complex, so it makes sense to map it to proper objects
// rather then manipulate JSON all along.

import { padStart } from "lodash";

export enum DayOfWeek {
    Monday = 1,
    Tuesday,
    Wednesday,
    Thursday,
    Friday,
    Saturday,
    Sunday
}

export function nameDay(day: DayOfWeek): string {
    switch (day) {
        case DayOfWeek.Monday:
            return "Poniedziałek";
        case DayOfWeek.Tuesday:
            return "Wtorek";
        case DayOfWeek.Wednesday:
            return "Środa";
        case DayOfWeek.Thursday:
            return "Czwartek";
        case DayOfWeek.Friday:
            return "Piątek";
        case DayOfWeek.Saturday:
            return "Sobota";
        case DayOfWeek.Sunday:
            return "Niedziela";
        default:
            return "";
    }
}

export type Hour = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
    14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23;
export type Minute = 0 | 15 | 30 | 45;
export type TimeTuple = [Hour, Minute];

// TermJSON is used to cast JSON into it and parse it into the proper Term class
// instance.
interface TermJSON {
    dayOfWeek: string;
    start_time: string;
    end_time: string;
    classrooms: string;
}

// Term is defined in apps/enrollment/models/term.py
export class Term {
    weekday: DayOfWeek;
    startTime: TimeTuple;
    endTime: TimeTuple;
    classrooms: string;
    constructor(json: TermJSON, public group: Group) {
        this.startTime = Term.parseTime(json.start_time);
        this.endTime = Term.parseTime(json.end_time);
        this.weekday = parseInt(json.dayOfWeek, 10) as DayOfWeek;
        this.classrooms = json.classrooms;
    }

    // Parses a timestamp (only time, no date) of format HH:MM:SS into a time
    // tuple. The function rounds down to quarters of an hour. This might not
    // give the closest quarter, but at least students will not be coming late.
    static parseTime(timestamp: string): TimeTuple {
        const sections = timestamp.split(":");
        if (sections.length !== 3) {
            throw new Error("Incorrect time format. Expected HH:MM:SS");
        }
        const hours: Hour = parseInt(sections[0], 10) as Hour;
        const minutesExact = parseInt(sections[1], 10);
        const minutes = (Math.floor(minutesExact / 15) * 15) as Minute;
        return [hours, minutes];
    }

    // Returns a string representation of a TimeTuple in H:MM format.
    static printTime(timeTuple: TimeTuple): string {
        const [hour, minute] = timeTuple;
        const zeroPrependedMinute = padStart(minute.toString(), 2, "0");
        return `${hour}:${zeroPrependedMinute}`;
    }

    get startTimeString(): string {
        return Term.printTime(this.startTime);
    }

    get endTimeString(): string {
        return Term.printTime(this.endTime);
    }
}

// Teacher is defined in apps/users/models.py as Employee, but we add the name
// field corresponding to `self.user.get_full_name()`.
export class Teacher {
    constructor(public name: string, public id: number, public url: string) {}
}

// Course is defined in apps/enrollment/courses/models/course.py.
export class Course {
    constructor(
        public name: string,
        public shortName: string,
        public url: string
    ) {}
}

export interface GuaranteedSpot {
    role: string;
    limit: number;
}

// GroupJSON is used to cast JSON into it and translate it into proper Group
// class instance.
export interface GroupJSON {
    id: number;
    num_enrolled: number;
    limit: number;
    extra: string;
    type: string;
    course: Course;
    teacher: Teacher;
    url: string;
    term: Array<TermJSON>;
    guaranteed_spots: Array<GuaranteedSpot>;

    is_enrolled?: boolean;
    is_enqueued?: boolean;
    is_pinned?: boolean;
    can_enqueue?: boolean;
    can_dequeue?: boolean;
    action_url?: string;
}

// Group is defined in apps/enrollment/courses/models/group.py.
export class Group {
    public id: number;
    public numEnrolled: number;
    public limit: number;
    public extra: string;
    public type: string;
    public course: Course;
    public teacher: Teacher;
    public url: string;
    public terms: Array<Term>;
    public guaranteedSpots: Array<GuaranteedSpot>;

    public isEnrolled = false;
    public isEnqueued = false;
    public isPinned = false;
    public isSelected = false;
    public canEnqueue = false;
    public canDequeue = false;

    // The URL for performing actions involving the group.
    public actionURL: string;

    constructor(json: GroupJSON) {
        this.id = json.id;
        this.numEnrolled = json.num_enrolled;
        this.limit = json.limit;
        this.extra = json.extra;
        this.type = json.type;
        this.course = json.course;
        this.teacher = json.teacher;
        this.url = json.url;
        this.terms = [];
        for (const term of json.term) {
            this.terms.push(new Term(term, this));
        }
        this.guaranteedSpots = json.guaranteed_spots;

        this.isEnrolled = json.is_enrolled || false;
        this.isEnqueued = json.is_enqueued || false;
        this.isPinned = json.is_pinned || false;
        this.canEnqueue = json.can_enqueue || false;
        this.canDequeue = json.can_dequeue || false;
        this.actionURL = json.action_url || "";
    }
}

export interface KVDict {
    [key: number]: string;
}

export interface PersonDict {
    [key: number]: [string, string]
}

export interface FilterDataJSON {
    allEffects: KVDict;
    allTags: KVDict;
    allOwners: PersonDict;
    allTypes: KVDict;
}
