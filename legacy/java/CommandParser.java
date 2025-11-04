import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class CommandParser {
    private Journal journal;

    public CommandParser(Journal journal) {
        this.journal = journal;
    }

    public void parseCommand(String input) {
        if (input.trim().equalsIgnoreCase("SHOW")) {
            journal.displayEntries();
        } else if (input.trim().toUpperCase().startsWith("ADD")) {
            // Use regex to capture the title and content inside quotes
            Pattern pattern = Pattern.compile("ADD \"(.*?)\" \"(.*?)\"");
            Matcher matcher = pattern.matcher(input);

            if (matcher.find()) {
                String title = matcher.group(1);
                String content = matcher.group(2);
                journal.addEntry(title, content);
                System.out.println("Entry added.");
            } else {
                System.out.println("Invalid ADD format. Use: ADD \"title\" \"content\"");
            }
        } else {
            System.out.println("Unknown command. Available commands: ADD, SHOW");
        }
    }
}
