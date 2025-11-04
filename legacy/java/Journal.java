import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.ArrayList;
import java.util.List;

public class Journal {
    private List<JournalEntry> entries;
    private static final String SAVE_FILE = "journal.dat";

    public Journal() {
        this.entries = new ArrayList<>();
        loadFromFile();
    }

    public void addEntry(String title, String content) {
        JournalEntry entry = new JournalEntry(title, content);
        entries.add(entry);
        saveToFile();
    }

    public void displayEntries() {
        for (JournalEntry entry : entries) {
            System.out.println(entry);
            System.out.println("---------------------");
        }
    }

    private void saveToFile() {
        try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(SAVE_FILE))) {
            oos.writeObject(entries);
        } catch (IOException e) {
            System.err.println("Error saving journal: " + e.getMessage());
        }
    }

    private void loadFromFile() {
        try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(SAVE_FILE))) {
            entries = (List<JournalEntry>) ois.readObject();
        } catch (IOException | ClassNotFoundException e) {
            // File might not exist yet, which is fine on first run.
            System.out.println("No previous journal found. Starting a new one.");
        }
    }

    public void exportEntries(String filename) {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filename))) {
            for (JournalEntry entry : entries) {
                writer.write(entry.getContent()); // or entry.toString() if you have a custom format
                writer.newLine();
                writer.write("-----");
                writer.newLine();
            }
            System.out.println("Entries exported to " + filename);
        } catch (IOException e) {
            System.out.println("Error exporting entries: " + e.getMessage());
        }
        }
    }

}
