import camelot
import re

# === Configuration ===
pdf_file = r"C:\GitHub\13flist2025q2.pdf"
output_txt = r"C:\GitHub\output12_final.txt"
output_csv = r"C:\GitHub\final_output_updated.csv"
DELIMITER = "|"  # You can change this to ',' or '\t' if needed

# === Step 1: Extract and Clean Tables from PDF ===
print("📄 Reading PDF tables...")
tables = camelot.read_pdf(pdf_file, flavor="stream", pages='3-end')

with open(output_txt, "w", encoding="utf-8") as f:
    for table in tables:
        df = table.df
        for _, row in df.iterrows():
            cleaned_row = [
                cell.replace("\n", " ").replace("\r", " ").strip()
                for cell in row
            ]
            f.write(f" {DELIMITER} ".join(cleaned_row) + "\n")

print(f"✅ Cleaned data written to: {output_txt}")

# === Step 2: Parse Cleaned Data and Write Final CSV ===
rows = []
total_count_from_file = None

with open(output_txt, "r", encoding="utf-8") as infile:
    for line in infile:
        line = line.strip()

        # ✅ Check for Total Count line
        match = re.search(r"Total\s+Count\s*:\s*([\d,]+)", line, re.IGNORECASE)
        if match:
            total_count_from_file = int(match.group(1).replace(",", ""))
            continue

        # ✅ Skip irrelevant lines
        if not line or line.startswith("Run") or line.startswith("CUSIP"):
            continue

        if line.count(DELIMITER) >= 3:
            # 🧱 Pipe-formatted row (special page format)
            parts = [part.strip() for part in line.split(DELIMITER)]
            if len(parts) < 3:
                continue
            raw_cusip = parts[0]
            cleaned_cusip = raw_cusip.replace(" ", "").replace("*", "")
            issuer = parts[1]
            description = parts[2]
            status = parts[3] if len(parts) > 3 else ""
        else:
            # 🪜 Fixed-width row
            pipe_index = line.find(DELIMITER)
            if pipe_index == -1:
                continue

            left_part = line[:pipe_index].ljust(60)
            right_part = line[pipe_index + 1:].strip()

            raw_cusip = left_part[:14].strip()
            cleaned_cusip = raw_cusip.replace(" ", "").replace("*", "")
            issuer = left_part[14:43].strip()
            description = left_part[43:pipe_index].strip()

            if "ADDED" in right_part:
                status = "ADDED"
            elif "DELETED" in right_part:
                status = "DELETED"
            else:
                status = ""

        # ✅ Ensure line doesn't start with | or ,
        if not cleaned_cusip or cleaned_cusip.startswith((DELIMITER, ",")):
            continue

        if cleaned_cusip and issuer and description:
            rows.append(DELIMITER.join([cleaned_cusip, issuer, description, status]))

# === Step 3: Write CSV Output ===
with open(output_csv, "w", encoding="utf-8") as outfile:
    outfile.write(DELIMITER.join(["CUSIP", "ISSUER", "DESCRIPTION", "STATUS"]) + "\n")
    for row in rows:
        outfile.write(row + "\n")

# === Step 4: Verify Total Count ===
actual_count = len(rows)

print(f"🔢 Rows written to CSV (excluding header): {actual_count}")
if total_count_from_file is not None:
    print(f"📋 Total Count from text file: {total_count_from_file}")
    if actual_count == total_count_from_file:
        print("✅ Row count matches the total count from file.")
    else:
        print("⚠️  Row count does NOT match the total count from file!")
else:
    print("⚠️  Total count line not found in the text file.")
