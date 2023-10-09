const FormWizard = VueFormWizard.FormWizard;
const TabContent = VueFormWizard.TabContent;
const ExampleSent = Vue.component('example-sent', {
    template: `
    <div class="ex-sent">
      <p class="sent-desc">Original Sentence (Human Written):</p>
      <div class="sent">
          <p><slot name="complex-sent"></slot></p>
      </div>
      <p class="sent-desc">Simplified Sentence (Human or AI Model Written):</p>
      <div class="sent">
          <p class="mb1"><slot name="simple-sent"></slot></p>
      </div>
      <template v-if="this.noedits == 'true'">
        <template v-if="this.explanation != undefined">
          <div class="explain no-edit-explain">
            {{ explanation }}
          </div>
        </template>
      </template><template v-else>
        <div class="edit-container">
          <slot name="edit"></slot>
          <template v-if="this.explanation != undefined">
            <div class="explain">
              {{ explanation }}
            </div>
          </template>
        </div>
      </template>
    </div>
    `,
    props: ['explanation', 'noedits'],
    created: function() {
      this.noedits = this.$props.noedits;
    }
});

const Sent = Vue.component('sent', {
  template: `<slot />`
});
const EditHeader = Vue.component('edit-header', {
  template: `
    <div class="f4 mt0 mb2 tc"> 
      <template v-if="this.type == 'deletion'">
        <span class="pa1 edit-text br-pill-ns border-deletion-all deletion_below txt-deletion">&nbsp;<slot name="span"></slot>&nbsp;</span>
      </template>
      <template v-if="this.type == 'insertion'">
        <span class="pa1 edit-text br-pill-ns border-insertion-all insertion_below txt-insertion">&nbsp;<slot name="span"></slot>&nbsp;</span>
      </template>
      <template v-if="this.type == 'substitution'">
        <span class="edit-type txt-substitution f3">substitute </span>
        <span class="pa1 edit-text br-pill-ns border-substitution-all substitution_below txt-substitution">&nbsp;<slot name="span"></slot>&nbsp;</span>
        <span class="edit-type txt-substitution f3">with </span>
        <span class="pa1 edit-text br-pill-ns border-substitution-all substitution_below txt-substitution">&nbsp;<slot name="span2"></slot>&nbsp;</span>
      </template>
      <template v-if="this.type == 'structural'">
        <span class="edit-type txt-structure f3">structure </span>
        <span class="pa1 edit-text br-pill-ns border-structure-all structure_below txt-structure">&nbsp;
          <i class="fa-solid fa-tree"></i> - <slot name="span"></slot> 
        </span> 
      </template>
      <template v-if="this.type == 'reorder'">
        <span class="edit-type txt-reorder f3">reorder </span>
        <span class="pa1 edit-text br-pill-ns border-reorder-all substitution_below txt-reorder">&nbsp;<slot name="span"></slot>&nbsp;</span>
        <span class="edit-type txt-reorder f3">to </span>
        <span class="pa1 edit-text br-pill-ns border-reorder-all substitution_below txt-reorder">&nbsp;<slot name="span2"></slot>&nbsp;</span>
      </template>
      <template v-if="this.type == 'split' && this.split_edit=='simple'">
        <span class="edit-type txt-split f3">split </span>
        <span class="pa1 edit-text br-pill-ns border-split-all split_below txt-split">&nbsp;||&nbsp;</span>
      </template>
      <template v-if="this.type == 'split' && this.split_edit=='deletion'">
        <span class="edit-type txt-split f3">split </span>
        <span class="pa1 edit-text br-pill-ns border-split-all split_below txt-split">&nbsp;||&nbsp;</span>
        <span class="edit-type txt-split f3">( delete </span>
        <span class="pa1 edit-text br-pill-ns border-split-all split_below txt-split">&nbsp;<slot name="span"></slot>&nbsp;</span>
        <span class="edit-type txt-split f3">)</span>
      </template>
      <template v-if="this.type == 'split' && this.split_edit=='insertion'">
        <span class="edit-type txt-split f3">split </span>
        <span class="pa1 edit-text br-pill-ns border-split-all split_below txt-split">&nbsp;||&nbsp;</span>
        <span class="edit-type txt-split f3">( insert </span>
        <span class="pa1 edit-text br-pill-ns border-split-all split_below txt-split">&nbsp;<slot name="span"></slot>&nbsp;</span>
        <span class="edit-type txt-split f3">)</span>
      </template>
      <template v-if="this.type == 'split' && this.split_edit=='insertion2'">
      <span class="edit-type txt-split f3">split </span>
      <span class="pa1 edit-text br-pill-ns border-split-all split_below txt-split">&nbsp;||&nbsp;</span>
      <span class="edit-type txt-split f3">( insert </span>
      <span class="pa1 edit-text br-pill-ns border-split-all split_below txt-split">&nbsp;<slot name="span"></slot>&nbsp;</span>
      <span class="edit-type txt-split f3"> , insert </span>
      <span class="pa1 edit-text br-pill-ns border-split-all split_below txt-split">&nbsp;But they&nbsp;</span>
      <span class="edit-type txt-split f3">)</span>
    </template>
      <template v-if="this.type == 'split' && this.split_edit=='substitution'">
        <span class="edit-type txt-split f3">split </span>
        <span class="pa1 edit-text br-pill-ns border-split-all split_below txt-split">&nbsp;||&nbsp;</span>
        <span class="edit-type txt-split f3">( substitute </span>
        <span class="pa1 edit-text br-pill-ns border-split-all split_below txt-split">&nbsp;<slot name="span"></slot>&nbsp;</span>
        <span class="edit-type txt-split f3">with</span>
        <span class="pa1 edit-text br-pill-ns border-split-all split_below txt-split">&nbsp;<slot name="span2"></slot>&nbsp;</span>
        <span class="edit-type txt-split f3">)</span>
      </template>
    </div>
  `,
  props: ['type', 'split_edit'],
  created: function() {
    this.type = this.$props.type;
    this.split_edit = this.$props.split_edit;
  }
});
const AnswerBox = Vue.component('answer-box', {
  data (){
    return {
      isAnswer: false,
      type: ''
    }
  },
  template: `
    <template v-if="this.type == 'deletion'">
      <div class="column-severity column-substitution w-10">
        <template v-if="interactive">
          <input class="checkbox-tools checkbox-tools-severity" type="radio" v-bind:id="editId*id" v-bind:name="editId">
        </template>
        <template v-else-if="isAnswer">
          <input class="checkbox-tools checkbox-tools-severity" type="radio" disabled checked>
        </template>
        <template v-else>
          <input class="checkbox-tools checkbox-tools-severity" type="radio" disabled>
        </template>
        <label class="for-checkbox-tools-severity question-deletion" v-bind:for="editId*id"> <slot></slot> </label>
      </div>
    </template>
    <template v-else-if="this.type == 'substitution'">
      <div class="column-severity column-substitution w-10">
        <template v-if="interactive">
          <input class="checkbox-tools checkbox-tools-severity" type="radio" v-bind:id="editId*id" v-bind:name="editId">
        </template>
        <template v-else-if="isAnswer">
          <input class="checkbox-tools checkbox-tools-severity" type="radio" disabled checked>
        </template>
        <template v-else>
          <input class="checkbox-tools checkbox-tools-severity" type="radio" disabled>
        </template>
        <label class="for-checkbox-tools-severity question-substitution" v-bind:for="editId*id"> <slot></slot> </label>
      </div>
    </template>
    <template v-else-if="this.type == 'grammar'">
      <div>
        <template v-if="isAnswer"><input class="checkbox-tools-yes-no" type="radio" name="insertion-yes-no" id="insertion-yes" value="yes" checked></template>
        <template v-else><input class="checkbox-tools-yes-no" type="radio" name="insertion-yes-no" id="insertion-yes" value="yes" checked></template>
        <label class="normal for-checkbox-tools-yes-no question-deletion"><slot></slot></label>
      </div>
    </template>
    <template v-else-if="this.type == 'insertion'">
      <div class="column-severity column-insertion w-10">
        <template v-if="isAnswer"><input class="checkbox-tools checkbox-tools-severity" type="radio" value="minor" disabled checked></template>
        <template v-else><input class="checkbox-tools checkbox-tools-severity" type="radio" value="minor" disabled></template>
        <label class="for-checkbox-tools-severity question-insertion" checked> <slot></slot> </label>
      </div>
    </template>
    <template v-else-if="this.type == 'structural'">
      <div class="column-severity column-structure w-10">
        <template v-if="isAnswer"><input class="checkbox-tools checkbox-tools-severity" type="radio" value="minor" disabled checked></template>
        <template v-else><input class="checkbox-tools checkbox-tools-severity" type="radio" value="minor" disabled></template>
        <label class="for-checkbox-tools-severity question-structure" checked> <slot></slot> </label>
      </div>
    </template>
    <template v-else-if="this.type == 'reorder'">
      <div class="column-severity column-structure w-10">
        <template v-if="isAnswer"><input class="checkbox-tools checkbox-tools-severity" type="radio" value="minor" disabled checked></template>
        <template v-else><input class="checkbox-tools checkbox-tools-severity" type="radio" value="minor" disabled></template>
        <label class="for-checkbox-tools-severity question-reorder" checked> <slot></slot> </label>
      </div>
    </template>
  `,
  props: ['isAnswer', 'type', 'interactive', 'id', 'editId', 'update'],
  created: function() {
    this.type = this.$props.type;
    this.isAnswer = this.$props.isAnswer;
    this.$props.interactive = this.$props.interactive ? this.$props.interactive=='true' ? true : false : false;

    if (this.$props.update) {
      this.$props.update(true);
    }
  }
});

const Edit = Vue.component('edit', {
  data (){
    return {
      answer: 0,
      question: '',
      explanation: '',
      subtypeQuestion: '',
      editId: 0,
      interactiveMessage: 'Please select an answer...'
    }
  },
  template: `
    <div>
      <div class="edit">
        <edit-header :type=type :split_edit=split_edit>
          <template #span>{{span}}</template>
          <template #span2>{{span2}}</template>
        </edit-header>

        <template v-if="this.reorder != ''">
          <p class="mb2 b tracked-light">
            What level is the reorder?
          </p>

          <div class="tc">
            <answer-box :isAnswer="this.reorder=='phrase'" :type=type>word-level</answer-box>
            <answer-box :isAnswer="this.reorder=='sentence'" :type=type>component-level</answer-box>
          </div>
        </template>

        <template v-if="this.subtype != '' && this.type == 'insertion'">
          <p class="mb2 b tracked-light">
            {{question}}
          </p>
          <div class="tc">
            <answer-box :isAnswer="this.subtype=='elaboration'" :type=type>Elaboration</answer-box>
            <answer-box :isAnswer="this.subtype=='trivial'" :type=type>Trivial Insertion</answer-box>
            <answer-box :isAnswer="this.subtype=='repetition'" :type=type>Repetition</answer-box>
            <answer-box :isAnswer="this.subtype=='contradiction'" :type=type>Contradiction</answer-box>
            <answer-box :isAnswer="this.subtype=='hallucination'" :type=type>Hallucination</answer-box>
          </div>

          <template v-if="this.irrelevant != ''">
            <p class="mb2 b tracked-light">
              Is the addition relevant to its context?
            </p>

            <div class="tc">
              <answer-box :isAnswer="this.irrelevant=='false'" :type=type>Yes</answer-box>
              <answer-box :isAnswer="this.irrelevant=='true'" :type=type>No</answer-box>
            </div>
          </template>
        </template>

        <template v-if="this.type == 'substitution'">
          <p class="mb2 b tracked-light">
            {{question}}
          </p>
          <div class="tc">
            <answer-box :isAnswer="this.subtype=='same'" :type=type>same meaning</answer-box>
            <answer-box :isAnswer="this.subtype=='less'" :type=type>less information</answer-box>
            <answer-box :isAnswer="this.subtype=='more'" :type=type>more information</answer-box>
            <answer-box :isAnswer="this.subtype=='different'" :type=type>different meaning</answer-box>
          </div>
        </template>

        <template v-if="this.subtype == 'same' && this.simplify != undefined">
          <p class="mb2 b tracked-light">
            Does the new phrase simplify the original phrase? 
            </p>
            <div class="tc grammar-answer">
            <answer-box :isAnswer="this.simplify=='true'" :type=type>yes</answer-box>
            <answer-box :isAnswer="this.simplify=='false'" :type=type>no</answer-box>
          </div>
        </template>

        <template v-if="this.subtype == 'less' && this.answer > 0">
          <p class="mb2 b tracked-light">
            Is the deleted information significant to the main idea of the original sentence?
            </p>
            <div class="tc">
              <answer-box :isAnswer="this.answer==1" :type=type>1 - not at all</answer-box>
              <answer-box :isAnswer="this.answer==2" :type=type>2 - minor</answer-box>
              <answer-box :isAnswer="this.answer==3" :type=type>3 - somewhat</answer-box>
              <answer-box :isAnswer="this.answer==4" :type=type>4 - very much</answer-box>
            </div>
        </template>

        <template v-if="this.coreference != ''">
          <p class="mb2 b tracked-light">
            Does the substitution remove a subject?
          </p>

          <div class="tc">
            <answer-box :isAnswer="this.coreference=='true'" :type=type>yes</answer-box>
            <answer-box :isAnswer="this.coreference=='false'" :type=type>no</answer-box>
          </div>
        </template>

        <template v-if="this.subtype == 'more' && this.instype != ''">
          <p class="mb2 b tracked-light">
            Select the type:
          </p>
          <div class="tc">
            <answer-box :isAnswer="this.instype=='elaboration'" :type=type>Elaboration</answer-box>
            <answer-box :isAnswer="this.instype=='trivial'" :type=type>Trivial Insertion</answer-box>
            <answer-box :isAnswer="this.instype=='repetition'" :type=type>Repetition</answer-box>
            <answer-box :isAnswer="this.instype=='contradiction'" :type=type>Contradiction</answer-box>
            <answer-box :isAnswer="this.instype=='hallucination'" :type=type>Hallucination</answer-box>

            <template v-if="this.answer > 0">
              <p class="mb2 b tracked-light">
                Rate the efficacy:
              </p>
              <div class="tc">
                <answer-box :isAnswer="this.answer==1" :type=type>1 - Minor</answer-box>
                <answer-box :isAnswer="this.answer==2" :type=type>2 - Somewhat</answer-box>
                <answer-box :isAnswer="this.answer==3" :type=type>3 - A lot</answer-box>
              </div>
            </template>
          </div>
        </template>

        <template v-if="this.subtype == 'more' && this.subsubtype == 'elaboration' && this.answer > 0">
          <p class="mb2 b tracked-light">
            How much the new information helps you to read and understand the sentence?
            </p>
            <div class="tc">
              <answer-box :isAnswer="this.answer==1" :type=type>1 - Minor</answer-box>
              <answer-box :isAnswer="this.answer==2" :type=type>2 - Somewhat</answer-box>
              <answer-box :isAnswer="this.answer==3" :type=type>3 - A lot</answer-box>
            </div>
        </template>

        <template v-if="this.subtype == 'different' && this.answer > 0">
          <p class="mb2 b tracked-light">
            How severe is this error?
            </p>
            <div class="tc">
              <answer-box :isAnswer="this.answer==1" :type=type>1 - Minor</answer-box>
              <answer-box :isAnswer="this.answer==2" :type=type>2 - Somewhat</answer-box>
              <answer-box :isAnswer="this.answer==3" :type=type>3 - A lot</answer-box>
            </div>
        </template>

        <template v-if="this.answer > 0 && this.type != 'substitution' && this.subtype != 'less' && this.subtype != 'more' && this.subtype != 'different'">
          <p class="mb2 b tracked-light">
            {{ subtypeQuestion }}
          </p>
          <template v-if="this.type == 'deletion'">
            <div class="tc">
              <answer-box :isAnswer="this.answer==1" :type=type :id=1 :editId=editId>1 - not at all</answer-box>
              <answer-box :isAnswer="this.answer==2" :type=type :id=2 :editId=editId>2 - minor</answer-box>
              <answer-box :isAnswer="this.answer==3" :type=type :id=3 :editId=editId>3 - somewhat</answer-box>
              <answer-box :isAnswer="this.answer==4" :type=type :id=4 :editId=editId>4 - very much</answer-box>
            </div>
          </template>
          <template v-if="this.type == 'insertion'">
            <div class="tc">
              <answer-box :isAnswer="this.answer==1" :type=type>1 - Minor</answer-box>
              <answer-box :isAnswer="this.answer==2" :type=type>2 - Somewhat</answer-box>
              <answer-box :isAnswer="this.answer==3" :type=type>3 - A lot</answer-box>
            </div>
          </template>
        </template>

        <template v-if="this.impact != ''">
          <p class="mb2 b tracked-light">
            How does the edit impact the simplicity of the phrase?
          </p>
          <div class="tc">
            <answer-box :isAnswer="this.impact=='positive'" :type=type :id=11 :editId=editId>positive</answer-box>
            <answer-box :isAnswer="this.impact=='none'" :type=type :id=12 :editId=editId>no impact</answer-box>
            <answer-box :isAnswer="this.impact=='negative'" :type=type :id=13 :editId=editId>negative</answer-box>
          </div>

          <template v-if="this.answer > 0">
            <p class="mb2 b tracked-light">
              <template v-if="this.impact=='positive'">
                Rate the efficacy:
              </template><template v-if="this.impact=='negative'">
                Rate the severity:
              </template>
            </p>
            <div class="tc">
              <answer-box :isAnswer="this.answer==1" :type=type>1 - Minor</answer-box>
              <answer-box :isAnswer="this.answer==2" :type=type>2 - Somewhat</answer-box>
              <answer-box :isAnswer="this.answer==3" :type=type>3 - A lot</answer-box>
            </div>
          </template>
          </template>
        </template>

        <template v-if="this.grammar != ''">
          <p class="mb2 b tracked-light">
            Does this deletion edit introduce any fluency / grammar error?
          </p>
          <div class="tc">
            <answer-box :isAnswer="this.grammar=='true'" :type=type>yes</answer-box>
            <answer-box :isAnswer="this.grammar=='false'" :type=type>no</answer-box>
          </div>
        </template>
      </div>
      <template v-if="this.explanation != ''">
        <div class="explain">
          {{ explanation }}
        </div>
      </template>
      <template v-if="this.interactive == 'true'">
        {{ interactiveMessage }}
      </template>
    </div>
    `,
    props: ['type', 'subtype', 'subsubtype', 'impact', 'instype', 'helptrivial', 'coreference', 'reorder', 'span', 'span2', 'answer', 'explanation', 'grammar', 'irrelevant', 'simplify', 'interactive', 'incorrectMessage', 'correctMessage', 'split_edit'],
    methods: {          
      getQuestion: function() {
        switch (this.$props.type) {
          case 'deletion':
            return 'Is the deleted span significant to the main idea of the original sentence?';
          case 'insertion':
            return 'Select the edit type:';
          case 'substitution':
            return 'Compared to the original phrase, the new phrase expresses:'
          default:
            return;
        }
      },
      getSubtypeQuestion: function() {
        switch (this.$props.subtype) {
          case 'elaboration':
          case 'trivial':
            return 'Rate the efficacy:';
          case 'hallucination':
          case 'error':
          case 'repetition':
          case 'contradiction':
            return 'Rate the severity:';
          case 'same':
            return 'Does the new phrase simplify the original phrase?';
          default:
            return this.$props.subtype;
        }
      },
      updateInteractiveMessage: function(isCorrect) {
        console.log(this.$props.correctMessage);
        this.interactiveMessage = isCorrect ? this.$props.correctMessage : this.$props.incorrectMessage;
      }
    },
    created: function() {
      this.question = this.getQuestion();
      this.subtypeQuestion = this.$props.type == 'deletion' ? this.question : this.getSubtypeQuestion();
      this.answer = parseInt(this.$props.answer);
      this.explanation = this.$props.explanation ? this.$props.explanation : ``;
      this.$props.subtype = this.$props.subtype ? this.$props.subtype : ``;
      this.$props.impact = this.$props.impact ? this.$props.impact : ``;
      this.$props.instype = this.$props.instype ? this.$props.instype : ``;
      this.$props.helptrivial = this.$props.helptrivial ? this.$props.helptrivial : ``;
      this.$props.grammar = this.$props.grammar ? this.$props.grammar : ``;
      this.$props.irrelevant = this.$props.irrelevant ? this.$props.irrelevant : ``;
      this.$props.interactive = this.$props.interactive ? this.$props.interactive : ``;
      this.$props.reorder = this.$props.reorder ? this.$props.reorder : ``;
      this.$props.coreference = this.$props.coreference ? this.$props.coreference : ``;
      this.editId = Math.floor(Math.random() * 100);
    }
});

const Substitution = Vue.component('es', {
  template: `<span class="bg-substitution-light substitution"><slot /></span>`
});
const Insertion = Vue.component('ei', {
  template: `<span class="bg-insertion-light insertion"><slot /></span>`
});
const Deletion = Vue.component('ed', {
  template: `<span class="bg-deletion-light deletion"><slot /></span>`
});
const Split = Vue.component('esp', {
  template: `<span class="bg-split-light split"><slot /></span>`
});
const Structure = Vue.component('est', {
  template: `<span class="bg-structure-light structure"><slot /></span>`
});
const UnderlinedStructure = Vue.component('ust', {
  template: `
  <template v-if="this.noto">
    <span class="structure pointer span simplified_span border-structure"><slot /></span>
  </template><template v-else>
    <span class="structure pointer span simplified_span outside border-structure"><slot /></span>
  </template>
  `,
  props: ['noto'],
  created: function() {
    this.noto = this.$props.noto != undefined;
  }
});
const SubscriptStructure = Vue.component('ss', {
  template: `
  <sub><i class="fa-solid fa-2xs txt-structure" style='padding-left: 3px'><slot /></i></sub>
  `
});
const SubscriptReorder = Vue.component('so', {
  template: `
  <sub><i class="fa-solid fa-2xs txt-reorder" style='padding-left: 3px'><slot /></i></sub>
  `
});
const Reorder = Vue.component('er', {
  template: `<span class="bg-reorder-light reorder"><slot /></span>`
});
const UnderlinedReorder = Vue.component('ur', {
  template: `
  <template v-if="this.o">
    <span class="reorder pointer span simplified_span outside border-reorder"><slot /></span>
  </template><template v-else>
    <span class="reorder pointer span simplified_span border-reorder"><slot /></span>
  </template>
  `,
  props: ['o'],
  created: function() {
    this.o = this.$props.o != undefined;
  }
});
const Todo = Vue.component('todo', {
  template: `<span class="todo"><slot /></span>`
});
const Quiz = Vue.component('quiz', {
  template: `
  <div>
    <img class="span_selection_quiz_answer" :id=id :src=imgsrc>
    <iframe :id=id :src=iframesrc width="100%" height="550" class="center db"></iframe>
    <div class="bb b--black-20 answer-container">
      <template v-if="this.answerExists == true">
        <a :id=id class="quiz-answer">See our answer →</a>
      </template>
    </div>
  </div>
  `,
  props: ['id', 'original', 'simplified'],
  created: function() {
    this.imgsrc = "./img/quiz-answers/" + this.$props.id + ".png"
    this.iframesrc = "quiz.html?original=" + this.$props.original + "&simplified=" + this.$props.simplified
    this.answerExists = true;
    $.ajax({
      url:this.imgsrc,
      type:'HEAD',
      error:function(){
        console.log('could not find ' + this.$props.id); 
        this.answerExists = false
      }, 
    });
  },
  mounted: function() {
    let ourId = this.$props.id;
    $('a#' + ourId).hover( function() {
      // show
      $('img#' + ourId).show();
    }, function() {
      $('img#' + ourId).css("display","none")
    })
  }
});

new Vue({
  el: '#app',
  components: {
    'form-wizard': FormWizard,
    'tab-content': TabContent,
    'example-sent': ExampleSent,
    'sent': Sent,
    'edit': Edit,
    'edit-header': EditHeader,
    'answer-box': AnswerBox,
    'es': Substitution,
    'ei': Insertion,
    'ed': Deletion,
    'esp': Split,
    'est': Structure,
    'er': Reorder,
    'todo': Todo,
    'quiz': Quiz
  },
  methods: {
    onComplete: function() {
      var iframe = document.getElementById("quiz_5_iframe");
      // console.log(iframe)
      var elmnt = iframe.contentWindow.document.getElementById("hits-data");
      let data = elmnt.innerHTML;
      console.log(data);
      // download data as json file
      var element = document.createElement('a');
      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(data));
      element.setAttribute('download', "quiz_5_hits.json");
      element.style.display = 'none';
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    },
    onChange: function() {
      $('html, body').animate({ scrollTop: 0 }, 'fast');

      // Allow dynamic resizing of iframes
      let resizeObservers = [];
      $('iframe').each(function () {
          // Add an offset for extra space after the iframe
          constant = 40;
          try {
            let observer = new ResizeObserver(entries => 
              this.height = this.contentWindow.document.body.scrollHeight + constant
            )
            observer.observe(this.contentWindow.document.body)
            resizeObservers.push(observer)
          } catch (e) {
            console.log(e)
          }
      })
    }
  },
  mounted() {
    var wizard = this.$refs.wizard
    wizard.activateAll()
  }
})

// Deletion Example Script
var contents_in = $('#bt-sent').html()
var contents_out = $('#bt-sent-out').html()

function addSpan(n, length) {
  $('#bt-sent').html(
    contents_in.substring(0, n) + '<span class=bg-deletion-light>' + contents_in.substring(n, n+length) + '</span>' + contents_in.substring(n+length)
  )
  $('#bt-sent-out').html(
    contents_in.substring(0, n) + contents_in.substring(n+length)
  )
}
function removeSpan() {
  $('#bt-sent').html(contents_in)
  $('#bt-sent-out').html(contents_out)
}

addSpan(18, 11)

$('#bt-1').mouseover(
    function() { 
      addSpan(18, 11) 
    }
)
$('#bt-2').mouseover(
  function() { addSpan(29, 8) }
)
$('#bt-3').mouseover(
  function() { addSpan(0, 38) }
)
$('#bt-4').mouseover(
  function() { addSpan(70, 11) }
)
$('#bt-5').mouseover(
  function() { addSpan(82, 16) }
)
$('#bt-6').mouseover(
  function() { addSpan(0, 38) }
)
$('#bt-7').mouseover(
  function() { addSpan(105, 37) }
)

$(".deletion-examples").mouseover(
  function() {
    // current background to red
    $(this).css("background-color", "#F4B8B1");
    // other background to white
    $(this).siblings().css("background-color", "#fff");
  }
);