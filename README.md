# Bayesian-Sentiment-Analysis

<h4>Created as part of course CS5100-Foundations of Artificial Intelligence at Northeastern University</h4>

<div>

<p><em>The base code in 'bt.py' other than the 'naive_bayes_classify()' and 'markov_model_classify()' function was provided by the professor of the course.</em></p><br>

<h3>Sentiment analysis of movie reviews</h3>
<p>The model is trained on data from www.kaggle.com/c/sentiment-analysis-on-movie-reviews. It predicts the most likely sentiment of a movie rating 
using a unigram (Naive Bayes) and bigram model (Markov model).</p><br>

<h3>Input</h3>
<h4>Input file pattern</h4>
1	1	happy happy joy joy	4<br>
2	2	happy meh joy meh	3<br>
3	3	meh meh meh meh	2<br>
4	4	blah meh blah meh	1<br>
5	5	blah ugh blah ugh	0<br>
---<br>
happy happy happy<br>
happy meh<br>
<h4>Explanation</h4>
<p>Lines before '---' are the training sentences with 'PhraseId',	'SentenceId',	'Phrase' and	'Sentiment'. Lines after it are to be classified.</p><br>


<h3>Output</h3>
<h4>Output file pattern:</h4>
4<br>
-3.6888794541139363<br>
4<br>
-3.6888794541139363<br>
3<br>
-3.6888794541139363<br>
3<br>
-2.995732273553991<br>
<h4>Explanation</h4>
<p>For each sentence to be classified from input file, there is one line each for the sentiment class and the logarithm probability obtained
from bayesian model and the same obtained from markovian model respectively. Hence, there are 4 lines for each sentence.</p><br>

<h3>Files included</h3>

<ol>
<li>by.py - Python code for the bayesian and markovian models</li>
<li>Text files 'bayesTest.txt', 'smallTest.txt', 'train.tsv' - Training data with sentences to be tested</li>
<li>Output files 'bayesTest.out', 'smallTest.out', 'train.out' - Output of the sentiment classification.</li>
</ol>

</div>
