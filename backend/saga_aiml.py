# saga_aiml.py
import aiml
import re
from Bio import Entrez, SeqIO, ExPASy, SwissProt

function_dict = {
    "Entrez.esearch": {"module": Entrez, "function_name": "esearch"},
    "Entrez.efetch": {"module": Entrez, "function_name": "efetch"},
    "SeqIO.parse": {"module": SeqIO, "function_name": "parse"},
    "ExPASy.get_sprot_raw": {"module": ExPASy, "function_name": "get_sprot_raw"},
    "SwissProt.read": {"module": SwissProt, "function_name": "read"}
}


def init_kernel():
    kernel = aiml.Kernel()
    kernel.learn("templates/startup.xml")
    kernel.learn("templates/menu.aiml")
    kernel.learn("templates/generic.aiml")
    kernel.learn("templates/biopython.aiml")
    return kernel, ""


def handle_input(kernel, user_input, last_topic):
    bot_response = kernel.respond(user_input, last_topic)

    if "<call>" in bot_response:
        match = re.search(r"<call>(.*)\.(.*)\((.*)\)</call>", bot_response)
        if match:
            module_name, function_name, arg_str = match.groups()
            args = [arg.strip() for arg in arg_str.split(",")]

            module = function_dict.get(f"{module_name}.{function_name}", {}).get("module")
            func = getattr(module, function_name, None) if module else None

            if func:
                try:
                    result = func(*args)
                    bot_response = bot_response.replace(match.group(0), str(result))
                except Exception as e:
                    bot_response = f"Function error: {str(e)}"

    elif "FETCH SEQUENCE" in user_input.upper():
        last_topic = "fetch_sequence"
        function_name = kernel.getPredicate("function_name")
        function_args = kernel.getPredicate("function_args")
        if function_name == "Entrez.esearch":
            Entrez.email = "your_email@example.com"
            handle = Entrez.esearch(db="pubmed", term=function_args)
            record = Entrez.read(handle)
            count = record["Count"]
            id_list = ",".join(record["IdList"])
            bot_response = kernel.respond("SEARCH RESULT").replace("{{count}}", str(count)).replace("{{id_list}}", id_list)

    elif last_topic == "fetch_sequence":
        gene_id = kernel.getPredicate("gene_id")
        if gene_id:
            if user_input.strip().lower() == "yes":
                handle = Entrez.efetch(db="nucleotide", id=gene_id, rettype="fasta", retmode="text")
                record = SeqIO.read(handle, "fasta")
                sequence = str(record.seq)
                bot_response = kernel.respond("SEQUENCE FOR *").replace("*", record.description)
                kernel.setPredicate("sequence_id", gene_id)
                kernel.setPredicate("sequence", sequence)
                bot_response += "\n" + sequence
            elif user_input.strip().lower() == "no":
                bot_response = "OK, let me know if you need anything else."
                kernel.setPredicate("gene_id", "")
            else:
                bot_response = f"Do you want me to retrieve the sequence for {gene_id}?"
        last_topic = ""

    return bot_response, last_topic
