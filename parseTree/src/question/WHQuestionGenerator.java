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
import edu.stanford.nlp.pipeline.CoreDocument;
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
    Set<String> personSet;
    Set<String> locationSet;
    Set<String> timeSet;

    public WHQuestionGenerator(String fileName, Set<String> escapeSet) {
        this.escapeSet = escapeSet;
        result = new ArrayList<>();
        // set up pipeline properties
        props = new Properties();
        props.put("annotators", "tokenize, ssplit, pos, lemma,ner");
        props.setProperty("ner.applyFineGrained", "false");
        props.setProperty("ner.useSUTime", "false");
        props.setProperty("ner.applyNumericClassifiers", "false");

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

        String file = loadFile(fileName);
        // make an example document
        CoreDocument doc = new CoreDocument(file);
        // // annotate the documents
        pipeline.annotate(doc);

        personSet = new HashSet<>();
        locationSet = new HashSet<>();
        timeSet = new HashSet<>();

        // test some locations because the NER location detector is not very
        // good
        locationSet.add("Ineb-Hedg");
        locationSet.add("Saqqara");

        // System.out.println(sentence);
        // if begin position is 0 and if it is after a comma, we put who infront
        for (CoreLabel elem : doc.tokens()) {

            if (elem.ner().equals("PERSON")) {
                personSet.add(elem.word());
            }
            if (elem.ner().equals("LOCATION")) {
                locationSet.add(elem.word());
            }
            if (elem.ner().equals("DATE")||elem.ner().equals("TIME")) {
                timeSet.add(elem.word());
            }
        }

        for (String d : timeSet) {
            System.out.println(d);
        }
        for (String sentence : sentences) {
            if (sentence.contains("References")) {
                break;
            }
            process(sentence);
        }
    }

    private void process(String sentence) {
        HashMap<Integer, List<TypedDependency>> subjMap = new HashMap<>();
        // get the lemma of the sentence
        List<String> lemmatized = lemmatize(sentence, pipeline);

        // Create StanfordCoreNLP object properties, with POS tagging
        // (required for lemmatization), and lemmatization

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
        String subj = null;
        int subjIndex = -1;

        // Depedency parse, What questions
        for (TypedDependency td : tdl) {
            // index of subj as key
            int key = td.gov().index();
            if (!subjMap.containsKey(key)) {
                subjMap.put(key, new ArrayList<>());
            }
            List<TypedDependency> relations = subjMap.get(key);
            relations.add(td);
            subj = null;
            subjIndex = -1;

            if (td.reln().toString().equals("nsubj") || td.reln().toString().equals("nsubjpass")) {
                // System.out.println("Nominal Subj relation: " + td);
                // subject with tagger
                // System.out.println(td.dep());
                subj = td.dep().originalText();
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

                // Generate where questions

                if (words[startIndex].equals("at")) {
                    if (locationSet.contains(words[startIndex + 1])) {
                        StringBuilder sb = new StringBuilder();
                        sb.append("Where did ");
                        sb.append(subj);
                        sb.append(" ");
                        sb.append(predicate);
                        sb.append("?");
                        result.add(sb.toString());
                    }

                }
                // Generate when questions

                if (sentence.contains("in") ||sentence.contains("on") ||sentence.contains("between") || sentence.contains("at")) {
                    Set<String> set = new HashSet<>(Arrays.asList(new String[]{"in", "on", "at", "between", "from", "to"}));
                    for(String time : timeSet) {
                        for (String pp : set) {
                            if (sentence.contains(pp + " " + time)) {
                                StringBuilder sb = new StringBuilder();
                                sb.append("When did ");
                                sb.append(subj);
                                sb.append(" ");
                                sb.append(predicate);
                                sb.append("?");
//                                System.out.println("when questions ----"+ sb.toString());
                                result.add(sb.toString());
                            }
                        }
                    }

                }

                if (subj.equals("which")) {
                    StringBuilder sb = new StringBuilder();
                    sb.append("What");
                    String[] subWords = Arrays.copyOfRange(words, startIndex - 1, words.length - 1);
                    for (String s : subWords) {

                        sb.append(" ");
                        sb.append(s);
                    }
                    String question = sb.toString().trim() + "?";
                    question = question.replaceAll(" ,", ",");
                    question = question.replaceAll(" '", "'");
                    question = question.replaceAll(" \\.", ".");
                    result.add(question);
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

        // generate who questions
        int indexWho = sentence.toLowerCase().indexOf("who");
        // if we found "who" inside the sentence, we can use it directly
        if (indexWho != -1) {
            StringBuilder sb = new StringBuilder();
            sb.append("Who ");
            String subString = sentence.substring(indexWho + 4, sentence.length() - 2);
            sb.append(subString);
            sb.append("?");

            String question = sb.toString().trim() + "?";
            question = question.replaceAll(" ,", ",");
            question = question.replaceAll(" '", "'");
            question = question.replaceAll(" \\.", ".");
            result.add(question);
            // else check if subj is a person, if it is, we can
            // generator Who questions
        } else if (personSet.contains(subj)) {
            StringBuilder sb = new StringBuilder();
            String[] subWords = Arrays.copyOfRange(words, subjIndex, words.length - 1);
            sb.append("Who");
            for (String s : subWords) {
                sb.append(" ");
                sb.append(s);
            }
            sb.append("?");
            // check for vague questions
            String[] chars = sb.toString().split("\\s+");
            if (!escapeSet.contains(chars[2])) {
                String question = sb.toString();
                question = question.replaceAll(" ,", ",");
                question = question.replaceAll(" '", "'");
                question = question.replaceAll(" \\.", ".");
                result.add(question);
            }

        }

        // generate what question
        generateQuestion(subjIndexes, tdl, subjMap, subjects, predicates);

        // System.out.println("***************************");

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
     * @param subjIndexes
     *            A list of indexes of Subjects found in the current sentence.
     * @param tdl
     *            Dependency tree generated by Stanford parser.
     * @param subjMap
     *            Map that stores the subjIndex as they key and a list of
     *            dependency relations that contains the subject index.
     * @param subjects
     *            A list of name of Subjects found in the current sentence.
     * @param predicates
     *            A list of predicates of Subjects found in the current
     *            sentence.
     *            <p>
     *            This method aims to add more detail to the generated question.
     *            It takes the above params to find if there exist any immediate
     *            modifier relations (amod, nmod, nummod, case) of the subject,
     *            It also goes down one more level to look for a second level
     *            modifier relations It then append these modifier phrases to
     *            the final question.
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

        // Set<String> whSet = new HashSet<>();
        // whSet.add("he");
        // whSet.add("who");
        // whSet.add("what");
        // whSet.add("that");
        // whSet.add("it");
        // whSet.add("this");

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
                String question = "What did " + subjects.get(i) + " " + predicates.get(i).trim() + "?";
                question = question.replaceAll(" ,", ",");
                question = question.replaceAll(" '", "'");
                question = question.replaceAll(" \\.", ".");
                result.add(question);
                // System.out.println(q);

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
            sb.append("What did ");
            for (int tmp : list) {
                sb.append(map.get(tmp) + " ");
            }
            sb.append(predicates.get(i).trim() + "?");
            String question = sb.toString();
            question = question.replaceAll(" ,", ",");
            question = question.replaceAll(" '", "'");
            question = question.replaceAll(" \\.", ".");
            result.add(question);
            // System.out.println(sb.toString());
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
