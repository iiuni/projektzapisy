// This small script downloads an example course proposal syllabus and puts its
// contents into the fields of proposal form as placeholders.

import axios from "axios";
import { safeLoad } from "js-yaml";
import * as $ from "jquery";

const EXAMPLE_SYLLABUS_URL = "/static/proposal/example-syllabus.yaml";

type map = {[key: string]: string | number};

// Gets example data from EXAMPLE_SYLLABUS_URL and fills the form placeholders
// with it.
async function get_data_and_fill_form() {
    try {
        const response = await axios.get(EXAMPLE_SYLLABUS_URL);
        const data = safeLoad(response.data) as map;
        for (let key in data) {
            $(`[name=${key}]`).attr("placeholder", (data[key] as string));
        }
    } catch (err) {
        console.log(err);
    }
}

$(document).ready(get_data_and_fill_form);
