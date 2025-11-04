import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Journal journal = new Journal();
        CommandParser parser = new CommandParser(journal);
        Scanner scanner = new Scanner(System.in);

        System.out.println("Journal App - Command Mode");
        System.out.println("Use: ADD \"title\" \"content\" | SHOW | EXIT");

        while (true) {
            System.out.print("> ");
            String command = scanner.nextLine();

            if (command.equalsIgnoreCase("EXIT")) {
                System.out.println("Exiting...");
                break;
            }

            parser.parseCommand(command);
        }
    }
}
