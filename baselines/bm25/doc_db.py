import sqlite3
import argparse
import time
import re
try:
    from retriever.utils import find_hyper_linked_titles, remove_tags, normalize
except:
    from utils import find_hyper_linked_titles, remove_tags, normalize


class DocDB(object):
    """Sqlite backed document storage.

    Implements get_doc_text(doc_id).
    """

    def __init__(self, db_path=None):
        self.path = db_path
        self.connection = sqlite3.connect(self.path, check_same_thread=False)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        """Close the connection to the database."""
        self.connection.close()

    def get_doc_ids(self):
        """Fetch all ids of docs stored in the db."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM documents")
        results = [r[0] for r in cursor.fetchall()]
        cursor.close()
        return results

    def get_doc_text(self, doc_id):
        """Fetch the raw text of the doc for 'doc_id'."""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT text FROM documents WHERE id = ?",
            (doc_id,)
        )
        result = cursor.fetchone()
        cursor.close()
        return result if result is None else result[0]

    def get_hyper_linked(self, doc_id):
        """Fetch the hyper-linked titles of the doc for 'doc_id'."""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT linked_title FROM documents WHERE id = ?",
            (doc_id,)
        )
        result = cursor.fetchone()
        cursor.close()
        return result if (result is None or len(result[0]) == 0) else [normalize(title) for title in result[0].split("\t")]

    def get_original_title(self, doc_id):
        """Fetch the original title name  of the doc."""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT original_title FROM documents WHERE id = ?",
            (doc_id,)
        )
        result = cursor.fetchone()
        cursor.close()
        return result if result is None else result[0]

    def get_doc_text_hyper_linked_titles_for_articles(self, doc_id):
        """
        fetch all of the paragraphs with their corresponding hyperlink titles.
        e.g., 
        >>> paras, links = db.get_doc_text_hyper_linked_titles_for_articles("Tokyo Imperial Palace_0")
        >>> paras[2]
        'It is built on the site of the old Edo Castle. The total area including the gardens is . During the height of the 1980s Japanese property bubble, the palace grounds were valued by some to be more than the value of all of the real estate in the state of California.'
        >>> links[2]
        ['Edo Castle', 'Japanese asset price bubble', 'Real estate', 'California']
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT text FROM documents WHERE id = ?",
            (doc_id,)
        )
        result = cursor.fetchone()
        cursor.close()
        if result is None:
            return [], []
        else:
            hyper_linked_paragraphs = result[0].split("\n\n")
            paragraphs, hyper_linked_titles = [], []

            for hyper_linked_paragraph in hyper_linked_paragraphs:
                paragraphs.append(remove_tags(hyper_linked_paragraph))
                hyper_linked_titles.append([normalize(title) for title in find_hyper_linked_titles(
                    hyper_linked_paragraph)])

            return paragraphs, hyper_linked_titles

    def get_doc_text_section_separations(self, doc_id):
        # WIP: we might have better formats to keep the information.
        """
        fetch all of the paragraphs with section level separations
        e.g., 
        >>> sectioned_paragraphs = db.get_doc_text_hyper_linked_titles_for_articles("Tokyo Imperial Palace_0")
        >>> sectioned_paragraphs[0]
        {"section_name":"Early life and sumo background.", 
        "parent_section_name": None:,
        "paragraphs": ["Tatsu Ryōya was born in Kanazawa, Ishikawa and is the youngest of three children. 
        His father was a truck driver. He was a normal-sized baby but grew quickly so that when 
        attending kindergarten he had difficulty fitting into the uniform. He first began 
        practicing sumo whilst in the first grade of elementary school.",
        "By the age of thirteen, when he ended his 
        first year at junior high school he stood , and weighed . 
        After competing successfully in junior high school sumo he gave up formal education 
        at the age of fifteen and entered the Takadagawa stable to pursue a professional career."
        "type": "child"}
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT text FROM documents WHERE id = ?",
            (doc_id,)
        )
        result = cursor.fetchone()
        cursor.close()
        if result is None:
            return []
        else:
            output_data = []
            section_separated_context = result[0].split("Section::::")

            parent_section = ""
            for s_idx, section in enumerate(section_separated_context):
                # the first sections are likely to be introductory paragraphs.
                if s_idx == 0 and len(section.split("\n\n")) > 1 and len(section.split("\n\n")[1]) > 0:
                    section_name = "Introduction"
                    parent_section = "Introduction"
                    output_data.append(
                        {"section_name": section_name, "paragraphs": section.split("\n\n")[1:],
                            "type": "intro", "parent_section_name": parent_section})
                else:
                    section_name = re.compile(
                        "(.*)\n").search(section).group(1)
                    section_text = re.sub("(.*)\n", "", section, 1)
                    if len(section_text) == 0:
                        # this is section header
                        parent_section = section_name
                        output_data.append({"section_name": section_name, "paragraphs": [],
                                            "type": "parent", "parent_section_name": None})
                    else:
                        output_data.append({"section_name": section_name, "paragraphs": [para for para in section_text.split("\n\n") if len(para) > 10],
                                            "type": "child", "parent_section_name": parent_section})
            return output_data
