package question;

import java.io.*;
import java.util.*;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.SentenceUtils;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.process.CoreLabelTokenFactory;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.process.PTBTokenizer;
import edu.stanford.nlp.process.Tokenizer;
import edu.stanford.nlp.process.TokenizerFactory;
import edu.stanford.nlp.trees.Tree;

/**
 * @author sisi
 */
public class BinaryQuestionGenerator {

    static Set<String> auxiliaries = new HashSet<>(Arrays.asList(new String[] {"am", "are", "is", "was", "were",
            "does", "did", "has", "had", "may", "might", "must",
            "need", "ought", "shall", "should", "will", "would"}));

    static List<String> sentences = new ArrayList<>();

    private final static String PCG_MODEL = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz";

    private final TokenizerFactory<CoreLabel> tokenizerFactory = PTBTokenizer.factory(new CoreLabelTokenFactory(),
            "invertible=true");

    private final LexicalizedParser parser = LexicalizedParser.loadModel(PCG_MODEL);


    public List<String> result;

    Set<String> escapeSet;

    BinaryQuestionGenerator(String fileName, Set<String> set) {
        this.escapeSet = set;
        result = new ArrayList<>();
        int count = 0;
        loadFile(fileName);
        for (String sentence : sentences) {
            if (sentence.contains("References")) {
                break;
            }
            process(sentence);
        }
        System.out.println("processed : " + count + " sentences.");
    }


    private void process(String sentence) {
//        System.out.println(sentence);

        Tree tree = parser.parse(sentence);

        List<Tree> leaves = tree.getLeaves();
        Map<String, String> verbTags = new HashMap<>();
        String auxiliaryVerb = "";
        for (Tree leaf : leaves) {
            // 1. find all verbs
            String tag = leaf.parent(tree).label().value();
            String word = leaf.value();
            Tree parent = leaf.parent(tree).parent(tree);
            if (leaf.parent(tree).label().value().contains("VB")) {
                if (auxiliaries.contains(word)) {
                    auxiliaryVerb = word;
                    Tree next = findChildAfter(parent, leaf.parent(tree));
                    if (next != null) {
                        // set first char to uppercase
                        char[] firstWord = auxiliaryVerb.toCharArray();
                        firstWord[0] = Character.toUpperCase(firstWord[0]);
                        auxiliaryVerb = new String(firstWord);
                        // create a question
                        String firstHalf = createString(parent.parent(tree).firstChild());
                        String lastHalf = createString(next);

                        // check escape words
                        String[] tmp = firstHalf.split("\\s");
                        if(escapeSet.contains(tmp[0])) {
                            continue;
                        }
                        String question = auxiliaryVerb + " " + firstHalf + " " + lastHalf.trim() + "?";
//                        System.out.println(question);

                        result.add(question);

//                        System.out.println(sentence);
//                        System.out.println(sentence);
//                        System.out.println(tree.score());
//                        System.out.println();
                    }
                } else {
                    verbTags.put(word, leaf.parent(tree).label().value());
                }
            }

        }


        // 2. if there's no auxiliary verb
        if (auxiliaryVerb.equals("")) {
            if (!verbTags.isEmpty()) {
                for (Map.Entry<String, String> entry : verbTags.entrySet()) {
                    if (entry.getValue().equals("VBD")) {
                        auxiliaryVerb = "Did";
                    } else if (entry.getValue().equals("VBZ")) {
                        auxiliaryVerb = "Does";
                    } else if (entry.getValue().equals("VBP")) {
                        auxiliaryVerb = "Do";
                    }
                }
                if (sentence.endsWith(" .")) {
                    sentence = sentence.substring(0, sentence.length()-1);
                }
                String q = auxiliaryVerb + " " + sentence.trim() + "?";
                result.add(q);
//                System.out.println("Question: " + auxiliaryVerb + " " + sentence);
            }
        }
    }

    public Tree parse(String str) {
        List<CoreLabel> tokens = tokenize(str);
        Tree tree = parser.apply(tokens);
        return tree;
    }

    private List<CoreLabel> tokenize(String str) {
        Tokenizer<CoreLabel> tokenizer = tokenizerFactory.getTokenizer(new StringReader(str));
        return tokenizer.tokenize();
    }

    private String createString(Tree tree) {
        StringBuilder sb = new StringBuilder();
        List<Tree> leaves = tree.getLeaves();
        for (int i = 0; i < leaves.size(); i++) {
            if (i == 0) {
                sb.append(leaves.get(i).value().toLowerCase() + " ");
            } else {
                sb.append(leaves.get(i).value()).append(" ");
            }
        }
        return sb.toString().substring(0, sb.length()-1);
    }


    public Tree findChildAfter(Tree parent, Tree target) {
        Tree[] children = parent.children();
        for (int i = 0; i < children.length; i++) {
            if (children[i] == target) {
                if ((i + 1) < children.length) {
                    return children[i+1];
                } else {
                    return null;
                }
            }
        }
        return null;
    }


    public void loadFile(String fileName) {
        Scanner fileInput = null;
        String fileContent = null;

        try {
            fileInput = new Scanner(new File(fileName));
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
        fileContent = fileInput.useDelimiter("\\A").next();
        // insert letters into a hashtable
        Reader reader = new StringReader(fileContent);
        DocumentPreprocessor dp = new DocumentPreprocessor(reader);

        for (List<HasWord> sentence : dp) {
            // SentenceUtils not Sentence
            String sentenceString = SentenceUtils.listToString(sentence);
            sentences.add(sentenceString);
        }
    }


    public List<String> getResult() {
        return result;
    }

    public void setResult(List<String> result) {
        this.result = result;
    }
}
