package question;

import java.io.*;
import java.util.*;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.Sentence;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.process.CoreLabelTokenFactory;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.process.PTBTokenizer;
import edu.stanford.nlp.process.Tokenizer;
import edu.stanford.nlp.process.TokenizerFactory;
import edu.stanford.nlp.trees.Tree;

public class BinaryQuestionGenerator {
    static Set<String> auxiliaries = new HashSet<>(Arrays.asList(new String[] {"am", "are", "is", "was", "were",
                                    "does", "did", "has", "had", "may", "might", "must",
                                    "need", "ought", "shall", "should", "will", "would"}));

    static String inputText = null;
    static List<String> sentences = new ArrayList<>();

    private final static String PCG_MODEL = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz";

    private final TokenizerFactory<CoreLabel> tokenizerFactory = PTBTokenizer.factory(new CoreLabelTokenFactory(),
            "invertible=true");

    private final LexicalizedParser parser = LexicalizedParser.loadModel(PCG_MODEL);

    public Tree parse(String str) {
        List<CoreLabel> tokens = tokenize(str);
        Tree tree = parser.apply(tokens);
        return tree;
    }

    private List<CoreLabel> tokenize(String str) {
        Tokenizer<CoreLabel> tokenizer = tokenizerFactory.getTokenizer(new StringReader(str));
        return tokenizer.tokenize();
    }

    public static void main(String[] args) {
        // print output
        PrintWriter writer = null;
        try {
            writer = new PrintWriter("questions", "UTF-8");
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        BinaryQuestionGenerator parser = new BinaryQuestionGenerator();
        int count = 0;
        parser.loadFile();
        for (String sentence : sentences) {
            if (sentence.contains("References")) {
                break;
            }
            System.out.println(sentence);

            Tree tree = parser.parse(sentence);

            // print the tree
//            tree.pennPrint();

            List<Tree> leaves = tree.getLeaves(); // Print words and Pos Tags
            Map<String, String> verbTags = new HashMap<>();
            String auxiliaryVerb = "";
            for (Tree leaf : leaves) {
//                 System.out.println(leaf);
                // get the individual's parent in the tree
                // X is Y, get X

//                if (leaf.parent(tree).label().value().equals("VBZ")) {
//                    Tree parent = leaf.parent(tree).parent(tree).parent(tree).firstChild();
//
//                    // System.out.println(parent.localTrees());
////                    System.out.println("What " + leaf.value());
//                    System.out.println(parent.getLeaves());
//                }

                // 1. find all verbs
                String tag = leaf.parent(tree).label().value();
                String word = leaf.value();
                Tree parent = leaf.parent(tree).parent(tree);
                if (leaf.parent(tree).label().value().contains("VB")) {
                    if (auxiliaries.contains(word)) {
                        auxiliaryVerb = word;
//                        findListNPBefore(parent, parent.parent(tree));
                        Tree next = parser.findChildAfter(parent, leaf.parent(tree));
                        if (next != null) {
                            // set first char to uppercase
                            char[] firstWord = auxiliaryVerb.toCharArray();
                            firstWord[0] = Character.toUpperCase(firstWord[0]);
                            auxiliaryVerb = new String(firstWord);
                            // create a question
                            String firstHalf = parser.createString(parent.parent(tree).firstChild());
                            String lastHalf = parser.createString(next);
                            String question = "--Question: " + auxiliaryVerb + " " + firstHalf + " " + lastHalf + "?";
                            System.out.println(question);
                            writer.println(sentence);
                            writer.println(question);
                            writer.println();
                        }
                        System.out.println();
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
                System.out.println("Question: " + auxiliaryVerb + " " + sentence);
                }
            }


            System.out.println("new sentence");
        }
        System.out.println("total count : " + count);
        writer.close();
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



    public void loadFile() {
        Scanner fileInput = null;
        String fileContent = null;

        try {
            fileInput = new Scanner(new File("data1.txt"));
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
        fileContent = fileInput.useDelimiter("\\A").next();
        // insert letters into a hashtable
        Reader reader = new StringReader(fileContent);
        DocumentPreprocessor dp = new DocumentPreprocessor(reader);

        for (List<HasWord> sentence : dp) {
            // SentenceUtils not Sentence
            String sentenceString = Sentence.listToString(sentence);
            sentences.add(sentenceString);

        }
        // sentences.add("The Old Kingdom is the period in the third
        // millennium.");

    }

}
