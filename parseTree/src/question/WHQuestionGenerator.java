package question;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.Reader;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Scanner;
import java.util.Set;

import edu.stanford.nlp.ling.CoreAnnotations.LemmaAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.SentenceUtils;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.process.CoreLabelTokenFactory;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.process.PTBTokenizer;
import edu.stanford.nlp.process.Tokenizer;
import edu.stanford.nlp.process.TokenizerFactory;
import edu.stanford.nlp.trees.GrammaticalStructure;
import edu.stanford.nlp.trees.GrammaticalStructureFactory;
import edu.stanford.nlp.trees.PennTreebankLanguagePack;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TreebankLanguagePack;
import edu.stanford.nlp.trees.TypedDependency;

public class WHQuestionGenerator {
    // LexicalizedParser lp =
    // LexicalizedParser.loadModel("edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz");

    TreebankLanguagePack tlp = new PennTreebankLanguagePack();
    GrammaticalStructureFactory gsf = tlp.grammaticalStructureFactory();
    Properties props;
    StanfordCoreNLP pipeline;

    public static List<String> sentences = new ArrayList<>();

    private final static String PCG_MODEL = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz";

    private final TokenizerFactory<CoreLabel> tokenizerFactory = PTBTokenizer.factory(new CoreLabelTokenFactory(),
            "invertible=true");

    private final LexicalizedParser parser = LexicalizedParser.loadModel(PCG_MODEL);

    List<String> result;
    Set<String> escapeSet;

    public WHQuestionGenerator(String fileName, Set<String> escapeSet) {
        this.escapeSet = escapeSet;
        result = new ArrayList<>();
        // set up pipeline properties
        props = new Properties();
        props.put("annotators", "tokenize, ssplit, pos, lemma");
        // props.setProperty("annotators", "tokenize,ssplit,pos,lemma,ner");

        // set up pipeline
        pipeline = new StanfordCoreNLP(props);

        // String[] sent = new String[] { "vladimir", "putin", "was", "born",
        // "in", "st.", "petersburg", "and", "he",
        // "was", "not", "born", "in", "berlin", "." };
        // Tree parse = parser.apply(Sentence.toWordList(sent));
        // GrammaticalStructure gs = gsf.newGrammaticalStructure(parse);
        // Collection<TypedDependency> tdl = gs.typedDependencies();
        // Tree dependTree = parser.parse(sent);
        // System.out.println(tdl);

        loadFile(fileName);
        for (String sentence : sentences) {
            if (sentence.contains("References")) {
                break;
            }
            process(sentence);
        }
    }

    private void process(String sentence) {
        HashMap<Integer, List<TypedDependency>> subjMap = new HashMap<>();
//        System.out.println(sentence);
        // get the lemma of the sentence
        List<String> lemmatized = lemmatize(sentence, pipeline);

        // Create StanfordCoreNLP object properties, with POS tagging
        // (required for lemmatization), and lemmatization

        // make an example document
        // CoreDocument doc = new CoreDocument(sentence);
        // // annotate the documents
        // pipeline.annotate(doc);
        // // view results
        // System.out.println("---");
        // System.out.println("entities found");
        // for (CoreEntityMention em : doc.entityMentions()) {
        // System.out.println("\tdetected entity: \t" + em.text() + "\t" +
        // em.entityType());
        // }
        // System.out.println("---");
        // System.out.println("tokens and ner tags");
        // String tokensAndNERTags = doc.tokens().stream().map(token -> "("
        // + token.word() + "," + token.ner() + ")")
        // .collect(Collectors.joining(" "));
        // System.out.println(tokensAndNERTags);

        Tree tree = parser.parse(sentence);
        GrammaticalStructure gs = gsf.newGrammaticalStructure(tree);
        Collection<TypedDependency> tdl = gs.typedDependencies();
        // System.out.println(tdl);
        List<Integer> subjIndexes = new ArrayList<>();
        List<String> subjects = new ArrayList<>();
        List<String> predicates = new ArrayList<>();
        String[] words = sentence.split("\\s+");

        Set<String> whereSet = new HashSet<>();
        // Where
        whereSet.add("at");
        whereSet.add("to");


        for (TypedDependency td : tdl) {
            // index of subj as key
            int key = td.gov().index();
            if (!subjMap.containsKey(key)) {
                subjMap.put(key, new ArrayList<>());
            }
            List<TypedDependency> relations = subjMap.get(key);
            relations.add(td);

            int subjIndex = -1;
            if (td.reln().toString().equals("nsubj") || td.reln().toString().equals("nsubjpass")) {
                // System.out.println("Nominal Subj relation: " + td);
                // subject with tagger
                // System.out.println(td.dep());
                String subj = td.dep().originalText();
                // System.out.println(td.dep().tag());
                subjIndex = td.dep().index();
                subjIndexes.add(subjIndex);
                subjects.add(subj);

                // System.out.println("subjIndex: " + subjIndex);

                // verb with tagger
                // String predicate = td.gov().originalText();
                int startIndex = td.gov().index();

                // get lemma of the predicate
                String predicate = lemmatized.get(startIndex - 1);

                // System.out.println(startIndex);

                predicates.add(predicate);

                if (subj.equals("which")) {
                    StringBuilder sb = new StringBuilder();
                    sb.append("What ");
                    String[] subWords = Arrays.copyOfRange(words, startIndex - 1, words.length - 1);
                    for (String s : subWords) {
                        sb.append(s);
                        sb.append(" ");
                    }
                    result.add(sb.toString().trim() + "?");
                    // System.out.println("What " + q);
                }


            }
            //
            // if (td.reln().toString().equals("pobject") &&
            // td.dep().index() == subjIndex) {
            // System.out.println("Nominal Subj relation: " + td);
            // for (CoreEntityMention em : doc.entityMentions()) {
            // if (em.text().equals(subjIndex)) {
            // System.out.println("found subj: " + em.text());
            // System.out.println("found subj ner: " + em.entityType());
            // }
            // }
            // }

        }

        generateQuestion(subjIndexes, tdl, subjMap, subjects, predicates);

//        System.out.println("***************************");

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

    public static List<String> lemmatize(String sentence, StanfordCoreNLP pipeline) {
        List<String> lemmas = new LinkedList<String>();

        // create an empty Annotation just with the given text
        Annotation document = new Annotation(sentence);

        // run all Annotators on this text
        pipeline.annotate(document);

        // Iterate over all tokens in a sentence
        for (CoreLabel token : document.get(TokensAnnotation.class)) {
            // Retrieve and add the lemma for each word into the list of
            // lemmas
            lemmas.add(token.get(LemmaAnnotation.class));

        }

        return lemmas;
    }


    /**
     * @param subjIndexes A list of indexes of Subjects found in the current sentence.
     * @param tdl         Dependency tree generated by Stanford parser.
     * @param subjMap     Map that stores the subjIndex as they key and a list of
     *                    dependency relations that contains the subject index.
     * @param subjects    A list of name of Subjects found in the current sentence.
     * @param predicates  A list of predicates of Subjects found in the current
     *                    sentence.
     *                    <p>
     *                    This method aims to add more detail to the generated question.
     *                    It takes the above params to find if there exist any immediate
     *                    modifier relations (amod, nmod, nummod, case) of the subject,
     *                    It also goes down one more level to look for a second level
     *                    modifier relations It then append these modifier phrases to
     *                    the final question.
     */
    private void generateQuestion(List<Integer> subjIndexes, Collection<TypedDependency> tdl,
                                         HashMap<Integer, List<TypedDependency>> subjMap, List<String> subjects, List<String> predicates) {
        Set<String> modifierSet = new HashSet<>();
        modifierSet.add("amod");
        modifierSet.add("nmod");
        modifierSet.add("nummod");
        modifierSet.add("case");
        modifierSet.add("advmod");
        modifierSet.add("mwe");

//        Set<String> whSet = new HashSet<>();
//        whSet.add("he");
//        whSet.add("who");
//        whSet.add("what");
//        whSet.add("that");
//        whSet.add("it");
//        whSet.add("this");

        if (subjIndexes == null || subjIndexes.isEmpty()) {
            return;
        }
        for (int i = 0; i < subjIndexes.size(); i++) {
            int index = subjIndexes.get(i);
            Map<Integer, String> map = new HashMap<>();
            List<Integer> list = new ArrayList<>();
            list.add(index);
            map.put(index, subjects.get(i));
            List<TypedDependency> deps = subjMap.get(index);
            if (deps == null || deps.isEmpty()) {
                // get the rest of the sentence starting with the predicate
                if (escapeSet.contains(subjects.get(i))) {
                    continue;
                }

                // what predicate.....? Who predicate .....?
                String q = "What did " + subjects.get(i) + " " + predicates.get(i).trim() + "?";
                result.add(q);
//                System.out.println(q);

                continue;
            }
            // loop through all dependencies of a subject
            for (TypedDependency dep : deps) {

                // System.out.println(dep.dep());
                int depIndex = dep.dep().index();
                // loop through all dependencies of a subject's dependency
                if (!modifierSet.contains(dep.reln().toString())) {
                    continue;
                }
                list.add(depIndex);
                map.put(depIndex, dep.dep().originalText());

                if (!subjMap.containsKey(depIndex)) {
                    continue;
                }
                for (TypedDependency subdep : subjMap.get(depIndex)) {
                    // System.out.println(subdep.reln().toString());
                    if (modifierSet.contains(subdep.reln().toString())) {
                        list.add(subdep.dep().index());
                        map.put(subdep.dep().index(), subdep.dep().originalText());
                        // System.out.println(subdep.dep());
                        // System.out.println(subdep.gov());
                        // list.add(subdep.dep().index()); // of
                        // list.add(subdep.gov().index()); // evidence
                        // list.add()
                    }
                }

            }

            // build question
            Collections.sort(list);
            StringBuilder sb = new StringBuilder();
            sb.append("what did ");
            for (int tmp : list) {
                sb.append(map.get(tmp) + " ");
            }
            sb.append(predicates.get(i).trim() + "?");
            result.add(sb.toString());
//            System.out.println(sb.toString());
        }

    }

    public String loadFile(String fileName) {
        Scanner fileInput = null;
        String fileContent;

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
        return fileContent;
    }

    public List<String> getResult() {
        return result;
    }

    public void setResult(List<String> result) {
        this.result = result;
    }
}
