import java.util.HashMap;
import java.util.Map;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.en.EnglishAnalyzer;
import org.apache.lucene.analysis.miscellaneous.PerFieldAnalyzerWrapper;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.util.Version;

public class CAnalyzer {
	
	PerFieldAnalyzerWrapper analyzer;
	private final Version matchVersion;
	
	public CAnalyzer(Version version) {
		matchVersion = version;
		
		Map<String, Analyzer> analyzerPerField = new HashMap<String, Analyzer>();
		//for option name
		analyzerPerField.put("op_name", new OptionNameAnalyzer(matchVersion));
		
		//for annotated option description
		analyzerPerField.put("op_desc", new EnglishAnalyzer(matchVersion));
		analyzer = new PerFieldAnalyzerWrapper(new StandardAnalyzer(matchVersion), analyzerPerField);
	}
	
	public Analyzer getAnalyzer() {
		return analyzer;
	}
}
