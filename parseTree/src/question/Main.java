package question;

import edu.stanford.nlp.pipeline.CoreNLPProtos;
import org.languagetool.JLanguageTool;
import org.languagetool.Language;
import org.languagetool.rules.RuleMatch;

import java.io.IOException;
import java.util.*;

/**
 * @author sisi on 11/14/18
 */
public class Main {


    public static void main(String[] args) throws IOException {
        String fileName = args[0];
        int limit = Integer.parseInt(args[1]);

        // add escape words.
        Set<String> escapeSet = new HashSet<>(Arrays.asList(new String[]{"he", "she", "him", "her", "me", "it", "who",
                                                    "this", "that", "which", "these", "those", "was"}));

        // generate questions
        BinaryQuestionGenerator binary = new BinaryQuestionGenerator(fileName, escapeSet);
        WHQuestionGenerator wh = new WHQuestionGenerator(fileName, escapeSet);

        List<String> results = new ArrayList<>();
        results.addAll(binary.getResult());
        results.addAll(wh.getResult());

        // rank
        List<MySentence> list = rank(results);

        for (int i = 0; i < limit; i++) {
            System.out.println(list.get(i).content);
        }

    }

    private static List<MySentence> rank(List<String> results) throws IOException {

        JLanguageTool langTool = new JLanguageTool(Language.getLanguageForName("English"));
        langTool.activateDefaultPatternRules();


        List<MySentence> list = new ArrayList<>();
        for (String r : results) {
            MySentence sen = new MySentence(r);
            list.add(sen);

            // decrease sentence that are too long.
            if (r.length() > 120) {
                sen.decrease(5);
            }

            // check spelling and grammar
            List<RuleMatch> matches = langTool.check(r);
            int errCnt = 0;
            for (RuleMatch match : matches) {
//                System.out.println("Potential error at line " +
//                        match.getEndLine() + ", column " +
//                        match.getColumn() + ": " + match.getMessage());
//                System.out.println("Suggested correction: " +
//                        match.getSuggestedReplacements());
                if (!match.getSuggestedReplacements().isEmpty() && !match.getSuggestedReplacements().get(0).equals(",")) {
                    errCnt++;
                }
            }
            sen.decrease(errCnt);
        }
        Collections.shuffle(list);
        Collections.sort(list, (s1, s2) -> s2.score - s1.score);
//        for (MySentence sentence : list) {
//            System.out.println("score: " + sentence.score + " " + sentence.content);
//            System.out.println(sentence.content);
//        }
        return list;
    }

    static class MySentence {
        String content;
        int score;
        public MySentence(String c){
            score = 10;
            content = c;
        }
        public void decrease(int s) {
            score -= s;
        }
    }
}
