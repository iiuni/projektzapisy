import json

import psycopg2
from loremipsum import generate_paragraph


def anonymize_poll(conn):
    """Performs anonymization of poll submissions.

    Function creates default answers from poll schemas and inserts
    them into proper poll submission entries.
    """
    cur = conn.cursor()
    # create answers from schemas
    query = "select PS.id, PS.questions from poll_schema PS"
    cur.execute(query)
    schemas = cur.fetchall()
    jsons_dict = dict()
    for row in schemas:
        json_src = row[1]
        for field in json_src['schema']:
            if field['type'] == 'textarea':
                field['answer'] = generate_paragraph()[2]
            elif field['type'] == 'radio':
                field['answer'] = field['choices'][0]
            json_dest = json.dumps(json_src)
            jsons_dict[row[0]] = json_dest
    # insert answers to sumbissions based on schema type
    query = "select SUB.id, SUB.schema_id from poll_submission SUB"
    cur.execute(query)
    polls = cur.fetchall()
    for row in polls:
        cur.execute("update poll_submission set answers = %s where id = %s",
                    (jsons_dict[row[1]], row[0]))
    cur.close()
    conn.commit()


def connect_and_anonymize(user, password, db_name, port):
    try:
        conn = psycopg2.connect(dbname=db_name, user=user,
                                password=password, host="localhost", port=port)
        anonymize_poll(conn)
    except psycopg2.Error:
        raise
