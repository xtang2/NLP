package question;

import edu.stanford.nlp.pipeline.CoreNLPProtos;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * @author sisi on 11/14/18
 */
public class Main {

    public static void main(String args[]) {
        String fileName = args[0];
        int limit = Integer.parseInt(args[1]);
        // generate questions
        BinaryQuestionGenerator binary = new BinaryQuestionGenerator(fileName);
        WHQuestionGenerator wh = new WHQuestionGenerator(fileName);

        List<String> results = new ArrayList<>();
        results.addAll(binary.getResult());
        results.addAll(wh.getResult());

        // rank
        List<MySentence> list = rank(results);

        for (int i = 0; i < limit; i++) {
            System.out.println(list.get(i).content);
        }
    }

    private static List<MySentence> rank(List<String> results) {

        List<Integer> len = new ArrayList<>();
        List<MySentence> list = new ArrayList<>();
        for (String r : results) {
            MySentence sen = new MySentence(r);
            list.add(sen);
            if (r.length() > 120) {
                sen.decrease(5);
            }
        }
        Collections.sort(list, (s1, s2) -> s2.score - s1.score);
        for (MySentence sentence : list) {
//            System.out.println("score: " + sentence.score + " " + sentence.content);
            System.out.println(sentence.content);
        }
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
