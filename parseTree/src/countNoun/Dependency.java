package countNoun;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.Reader;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Scanner;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.Sentence;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.process.CoreLabelTokenFactory;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.process.PTBTokenizer;
import edu.stanford.nlp.process.Tokenizer;
import edu.stanford.nlp.process.TokenizerFactory;
import edu.stanford.nlp.trees.EnglishGrammaticalRelations;
import edu.stanford.nlp.trees.GrammaticalStructure;
import edu.stanford.nlp.trees.GrammaticalStructureFactory;
import edu.stanford.nlp.trees.PennTreebankLanguagePack;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TreebankLanguagePack;
import edu.stanford.nlp.trees.TypedDependency;

public class Dependency {
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
        // LexicalizedParser lp =
        // LexicalizedParser.loadModel("edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz");

        TreebankLanguagePack tlp = new PennTreebankLanguagePack();
        GrammaticalStructureFactory gsf = tlp.grammaticalStructureFactory();

        // String[] sent = new String[] { "vladimir", "putin", "was", "born",
        // "in", "st.", "petersburg", "and", "he",
        // "was", "not", "born", "in", "berlin", "." };
        // Tree parse = parser.apply(Sentence.toWordList(sent));
        // GrammaticalStructure gs = gsf.newGrammaticalStructure(parse);
        // Collection<TypedDependency> tdl = gs.typedDependencies();
        // Tree dependTree = parser.parse(sent);
        // System.out.println(tdl);

        Dependency parser = new Dependency();
        int count = 0;
        parser.loadFile();
        for (String sentence : sentences) {
            System.out.println(sentence);
            Tree tree = parser.parse(sentence);
            GrammaticalStructure gs = gsf.newGrammaticalStructure(tree);
            Collection<TypedDependency> tdl = gs.typedDependencies();
            System.out.println(tdl);

            for (TypedDependency td : tdl) {
                if (td.reln().equals(EnglishGrammaticalRelations.NOMINAL_SUBJECT)) {
                    System.out.println("Nominal Subj relation: " + td);
                }
                if (td.reln().equals(EnglishGrammaticalRelations.PREPOSITIONAL_OBJECT)) {
                    System.out.println("Nominal Subj relation: " + td);
                }

                if (td.reln().toString().equals("nsubjpass")) {
                    System.out.println("Passive Nominal Subj relation: " + td);
                }

            }
            System.out.println("***************************");
            // print the tree

            List<Tree> leaves = tree.getLeaves(); // Print words and Pos Tags

            for (Tree leaf : leaves) {
                // System.out.println(leaf);
                // get the individual's parent in the tree
                // X is Y, get X
                // what is, what has,

                if (leaf.parent(tree).label().value().equals("VBZ")) {
                    Tree parent = leaf.parent(tree).parent(tree).parent(tree).firstChild();

                    // System.out.println(parent.localTrees());
                    // System.out.println("What is ");
                    // System.out.println(parent.getLeaves());
                }

                // parent.label().value() + " ");
                /*
                 * if (parent.label().value().equals("VBZ")) {
                 * System.out.println(leaf.label().value());
                 * System.out.println(parent.parent(tree).firstChild());
                 * 
                 * }
                 */
            }

            // System.out.println("new sentence");
        }
        // System.out.println("total count : " + count);

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
