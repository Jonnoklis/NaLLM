def get_fewshot_examples(openai_api_key):
    return f"""
# Zoek alle documenten met tabellen tussen 1 juli 2022 en 30 september 2022.
MATCH (v:volledig_document)-[r:`bevat tabel`]->(t:tabel_rij)
WHERE date(v.factuurdatum) >= date("2022-07-01") AND date(v.factuurdatum) <= date("2022-09-30")
RETURN v, r, t

# Haal alle documenten op met tabellen.
MATCH (v:volledig_document)-[r:`bevat tabel`]->(t:tabel_rij)
RETURN v, r, t

# Zoek documenten op basis van een specifiek factuurnummer.
MATCH (v:volledig_document)-[r:`bevat tabel`]->(t:tabel_rij)
WHERE v.factuurnummer = "20222544"
RETURN v, r, t

# Vind documenten waar het totaalbedrag meer dan 1000 is.
MATCH (v:volledig_document)-[r:`bevat tabel`]->(t:tabel_rij)
WHERE v.totaalbedrag > 1000
RETURN v, r, t

# Zoek documenten waar het totaalbedrag meer dan 1000 is en tabelbedrag meer dan 50.
MATCH (v:volledig_document)-[r:`bevat tabel`]->(t:tabel_rij)
WHERE v.totaalbedrag > 1000 AND t.tabel_Bedrag > 50
RETURN v, r, t

# Vind documenten op basis van een specifieke bankrekening.
MATCH (v:volledig_document)-[r:`bevat tabel`]->(t:tabel_rij)
WHERE v.bank = "NL20INGB0009399930"
RETURN v, r, t

# Filter op basis van gewerkte uren: haal records op waar tabel_Aantal (uren) meer dan 1 is.
MATCH (v:volledig_document)-[r:`bevat tabel`]->(t:tabel_rij)
WHERE t.tabel_Aantal > 1
RETURN v, r, t"""
