from datasheets import *
from file_prompt import filenames
from text_manipulation import *
from unidecode import unidecode

if __name__ == "__main__":
    # prompt user for CSV file names- one to read from and one to write to. Can be
    print("Welcome to the datasheet tool.")
    (file_in, file_out) = filenames()
    print("\nIf AllDatasheet doesn't return a great match, the script will ask you to review them one at a time during "
          "the search. You may choose to automatically mark these for review instead. You can fix those items in the "
          "spreadsheet after it finishes exporting.")
    automatic_mark_for_review = prompt_yes_no("Automatically mark bad items for review?",False)
    print("\nYou can use the regular UTF-8 character set or limit results to ASCII characters only.")
    utf8_characters_allowed = prompt_yes_no("Use standard UTF-8 character set?",True)


    # parse the file to get a list of parts
    print("\nLoading your file...")
    parts = get_part_numbers_from_csv(file_in)

    # some interface and formatting
    j = len(parts)
    print("Found {} parts in file.".format(j))
    print(" ")

    # look up each part
    res = []
    for i in range(len(parts)):
        hyperlink_text = "datasheet"
        part = parts[i]
        print_same_line(
            "Downloading data from AllDatasheet ({}/{}, {} remaining)".format(i + 1, j,
                                                                              estimated_time_completion(i,
                                                                                                        j,
                                                                                                        avg_time=1)))
        # make the request and get the HTML content
        html = get_html_from_alldatasheet(part)
        # Parse the results table from the DOM
        main_table = get_item_table(html)
        # extract the data
        descriptions = get_part_descriptions(main_table)
        url = get_datasheet_link(main_table)
        # Make a CSV formatted line with the format:
        # [part number], [url], [description 1], [description 2], [description 3]
        description = pick_best_description(part, descriptions, automatic_mark_for_review)
        if description is None:
            description = "** Please review **"
            hyperlink_text = "REVIEW"
        res.append(
            ",".join([clean_text(part), '"=HYPERLINK(""{}"",""{}"")"'.format(url, hyperlink_text), '"{}"'.format(description)]))

    # interface
    print_same_line("Downloaded {} part details.".format(j))

    print("Saving to {}...".format(file_out))

    # write to file
    with open(file_out, 'w', encoding='utf-8') as f:
        for line in res:
            if utf8_characters_allowed:
                f.write(line)
            else:
                f.write(unidecode(line))
            f.write("\n")
    print("Saved file.")
