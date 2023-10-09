const app = Vue.createApp({
    data() {
        return {
            total_hits: 0,
            current_hit: 1,
            hits_data: null,
            original_html: '',
            simplified_html: '',
            edits_html: '',
            edits_dict: {'deletion': {}, 'substitution': {}, 'insertion': {}, 'split':{}, 'reorder':{}, 'structure':{}},
            single_edit_html: '',
            enable_select_original_sentence: false,
            enable_select_simplified_sentence: false,
            selected_span_in_original: '',
            selected_span_in_simplified: '',
            selected_span_in_original_indexs: [],
            selected_span_in_simplified_indexs: [],

            // selected_edits_html is for split and structure edits
            selected_edits_html: "",
            selected_edits: {'deletion': {}, 'insertion': {}, 'substitution': {}, 'reorder':{}},
            selected_split: '',
            selected_split_id: null,

            // for deletion annotation box
            deletion_severity_box: "",
            deletion_grammar_yes_no_box: "",
            deletion_coref_yes_no_box: "",

            // for insertion annotation box
            insertion_type_box: "",
            insertion_elaboration_severity_box: "",
            insertion_trivial_yes_no_box: "",
            insertion_trivial_severity_box: "",
            insertion_repetition_severity_box: "",
            insertion_contradiction_severity_box: "",
            insertion_hallucination_severity_box: "",
            insertion_hallucination_relevance_yes_no_box: "",
            insertion_trivial_yes_no_box: "",
            insertion_grammar_yes_no_box: "",

            // for substitution annotation box
            substitution_type_box: "",
            substitution_simplify_yes_no_box: "",
            substitution_impact_box: "",
            substitution_less_severity_box: "",
            substitution_more_type_box: "",
            substitution_elaboration_severity_box: "",
            substitution_repetition_severity_box: "",
            substitution_trivial_severity_box: "",
            substitution_trivial_yes_no_box: "",
            substitution_contradiction_severity_box: "",
            substitution_hallucination_severity_box: "",
            substitution_different_severity_box: "",
            substitution_positive_severity_box: "",
            substitution_hallucination_relevance_yes_no_box: "",
            substitution_negative_severity_box: "",
            substitution_grammar_yes_no_box: "",
            substitution_coref_yes_no_box: "",

            // for split annotation box
            split_impact_box: "",
            split_negative_severity_box: "",
            split_positive_severity_box: "",
            split_grammar_yes_no_box: "",

            // for reorder annotation box
            reorder_impact_box: "",
            reorder_positive_severity_box: "",
            reorder_negative_severity_box: "",
            reorder_grammar_yes_no_box: "",
            reorder_level_box: "",

            // for structure annotation box
            structure_impact_box: "",
            structure_positive_severity_box: "",
            structure_negative_severity_box: "",
            structure_grammar_yes_no_box: "",
            

            lines: {"split":{}, "substitution":{}, "reorder":{}, "structure":{}},
            current_insertion_deletion_pair: null,
            open : false,
            open_annotation : false,
            category_to_id: {'deletion': 0, 'substitution': 1, 'split': 2, 'insertion': 3, 'reorder': 4, 'structure': 5},
            id_to_category: {0: 'deletion', 1: 'substitution', 2: 'split', 3:'insertion', 4: 'reorder', 5: 'structure'},
            key_to_key_short: {'deletion': 'delete', 'substitution': 'substitute', 'split': 'split', 'insertion': 'insert', 'reorder': 'reorder', 'structure': 'structure'},

            current_insertion_edit_id : null,

            // connect_delete_click : false,
            clicked_deletion: "",

            annotating_edit_span_in_original: '',
            annotating_edit_span_in_simplified: '',
            annotating_edit_span_for_split: '',
            annotating_edit_span_for_structure: '',
            annotating_edit_span_category_id: -1,
        }
    },
    methods: {
        process_original_html() {
            let prev_idx = 0
            let sentence_html = ''
            let original_sentence = this.hits_data[this.current_hit - 1].original
            let original_spans = this.hits_data[this.current_hit - 1].original_spans
            original_spans.sort(function(a, b) {
                return a[1] - b[1] || b[2] - a[2];
            });
            // iterate original_spans list
            for (let i = 0; i < original_spans.length; i++) {
                sentence_html += original_sentence.substring(prev_idx, original_spans[i][1]);
                let light = "-light"
                let original_span_id = original_spans[i][3]
                if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (original_span_id in this.hits_data[[this.current_hit - 1]].annotations[this.id_to_category[original_spans[i][0]]])) {
                    light = ""
                }
                let outside = ""
                if (i < original_spans.length - 1 && original_spans[i + 1][1] <= original_spans[i][2]) {
                    outside = "outside"
                }
                let category = this.id_to_category[original_spans[i][0]]
                if (category == "split" || category == "structure") {
                    let childcategory = this.id_to_category[original_spans[i][4]]
                    let childid = original_spans[i][5]
                    sentence_html += `<span @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${category} border-${category}${light} pointer span original_span ${outside}" data-category="${category}" data-id="${category}-` + original_span_id + `" data-childcategory=${childcategory} data-childid=${childid}>`;
                } else {
                    sentence_html += `<span @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${category} border-${category}${light} pointer span original_span ${outside}" data-category="${category}" data-id="${category}-` + original_span_id + `">`;
                }
                let start_i = i
                let whether_more_overlap = false
                while (i < original_spans.length - 1 && original_spans[i + 1][1] <= original_spans[start_i][2]) {
                    // the next span is in the current span
                    let next_span = original_spans[i + 1]
                    if (i == start_i) {
                        sentence_html += original_sentence.substring(original_spans[i][1], next_span[1]);
                    } else {
                        if (whether_more_overlap) {
                            sentence_html += original_sentence.substring(original_spans[i-1][2], next_span[1]);
                        } else {
                            sentence_html += original_sentence.substring(original_spans[i][2], next_span[1]);
                        }
                    }
                    whether_more_overlap = false             
                    let next_category = this.id_to_category[next_span[0]]
                    let outside = ""
                    if (i < original_spans.length - 2 && original_spans[i + 2][1] <= original_spans[i+1][2]) {
                        outside = "middleside"
                    }
                    let light = "-light"
                    let original_span_id = next_span[3]
                    if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (original_span_id in this.hits_data[[this.current_hit - 1]].annotations[this.id_to_category[next_span[0]]])) {
                        light = ""
                    }
                    if (next_category == "split" || next_category == "structure") {
                        let childcategory = this.id_to_category[next_span[4]]
                        let childid = next_span[5]
                        sentence_html += `<span @mouseover.stop @mouseout.stop @click.stop @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${next_category} border-${next_category}${light} pointer span original_span ${outside}" data-category="${next_category}" data-id="${next_category}-` + next_span[3] + `" data-childcategory=${childcategory} data-childid=${childid}>`;
                    } else {
                        sentence_html += `<span @mouseover.stop @mouseout.stop @click.stop @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${next_category} border-${next_category}${light} pointer span original_span ${outside}" data-category="${next_category}" data-id="${next_category}-` + next_span[3] + `">`;
                    }
                    i++;
                    if (i < original_spans.length - 1 && original_spans[i + 1][1] <= original_spans[i][2]) {
                        whether_more_overlap = true
                        // the next span is in the current span
                        let next_next_span = original_spans[i + 1]
                        sentence_html += original_sentence.substring(original_spans[i][1], next_next_span[1]);  
                        let next_category = this.id_to_category[next_next_span[0]]
                        let light = "-light"
                        let original_span_id = next_next_span[3]
                        if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (original_span_id in this.hits_data[[this.current_hit - 1]].annotations[this.id_to_category[next_next_span[0]]])) {
                            light = ""
                        }
                        if (next_category == "split" || next_category == "structure") {
                            let childcategory = this.id_to_category[next_next_span[4]]
                            let childid = next_next_span[5]
                            sentence_html += `<span @mouseover.stop @mouseout.stop @click.stop @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${next_category} border-${next_category}${light} pointer span original_span" data-category="${next_category}" data-id="${next_category}-` + next_next_span[3] + `" data-childcategory=${childcategory} data-childid=${childid}>`;
                        } else {
                            sentence_html += `<span @mouseover.stop @mouseout.stop @click.stop @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${next_category} border-${next_category}${light} pointer span original_span" data-category="${next_category}" data-id="${next_category}-` + next_next_span[3] + `">`;
                        }
                        sentence_html += original_sentence.substring(next_next_span[1], next_next_span[2]);
                        sentence_html += "</span>";
                        sentence_html += original_sentence.substring(next_next_span[2], original_spans[i][2]);
                        console.log(original_sentence.substring(next_next_span[2], original_spans[i][2]))
                        sentence_html += `</span>`;
                        i++;
                    } else {
                        sentence_html += original_sentence.substring(next_span[1], next_span[2]);
                        sentence_html += "</span>";
                    }
                }
                if (start_i != i) {
                    if (whether_more_overlap) {
                        sentence_html += original_sentence.substring(original_spans[i - 1][2], original_spans[start_i][2]);
                    } else {
                        sentence_html += original_sentence.substring(original_spans[i][2], original_spans[start_i][2]);
                    }
                    sentence_html += `</span>`;
                    prev_idx = original_spans[start_i][2];
                } else {
                    sentence_html += original_sentence.substring(original_spans[i][1], original_spans[i][2]);
                    sentence_html += `</span>`;
                    prev_idx = original_spans[i][2];
                }
            }
            sentence_html += original_sentence.substring(prev_idx);
            this.original_html = sentence_html;
        },
        process_original_html_with_selected_span(category, start, end) {
            this.selected_span_in_original_indexs = [start, end]
            let prev_idx = 0
            let sentence_html = ''
            let original_sentence = this.hits_data[this.current_hit - 1].original
            let original_spans = JSON.parse(JSON.stringify(this.hits_data[this.current_hit - 1].original_spans))
            let category_id = this.category_to_id[category]
            original_spans.push([category_id, start, end]);
            // rank original_spans list by [1]
            original_spans.sort(function(a, b) {
                return a[1] - b[1] || b[2] - a[2];
            });
            // iterate original_spans list
            for (let i = 0; i < original_spans.length; i++) {
                sentence_html += original_sentence.substring(prev_idx, original_spans[i][1]);
                let span_category = this.id_to_category[original_spans[i][0]]
                let outside = ""
                if (i < original_spans.length - 1 && original_spans[i + 1][1] <= original_spans[i][2]) {
                    outside = "outside"
                }
                if (original_spans[i][1] == start && original_spans[i][2] == end) {
                    sentence_html += `<span @mouseover.stop @mouseout.stop class="bg-${span_category}-light span ${outside}">`;
                } else {
                    let light = "-light"
                    let original_span_id = original_spans[i][3]
                    if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (original_span_id in this.hits_data[[this.current_hit - 1]].annotations[span_category])) {
                        light = ""
                    }
                    sentence_html += `<span @mouseover="hover_span" @mouseout="un_hover_span" class="${span_category} border-${span_category}${light} pointer span original_span ${outside}" data-category="${span_category}" data-id="${span_category}-` + original_span_id + `">`;
                }
                let start_i = i
                let whether_more_overlap = false
                while (i < original_spans.length - 1 && original_spans[i + 1][1] <= original_spans[start_i][2]) {
                    // the next span is in the current span
                    let next_span = original_spans[i + 1]
                    if (i == start_i) {
                        sentence_html += original_sentence.substring(original_spans[i][1], next_span[1]);
                    } else {
                        if (whether_more_overlap) {
                            sentence_html += original_sentence.substring(original_spans[i - 1][2], next_span[1]);
                        } else {
                            sentence_html += original_sentence.substring(original_spans[i][2], next_span[1]);
                        }
                    }
                    whether_more_overlap = false               
                    let next_category = this.id_to_category[next_span[0]]
                    let outside = ""
                    if (i < original_spans.length - 2 && original_spans[i + 2][1] <= original_spans[i+1][2]) {
                        outside = "middleside"
                    }
                    if (next_span[1] == start && next_span[2] == end) {
                        sentence_html += `<span @mouseover.stop @mouseout.stop class="bg-${next_category}-light span ${outside}">`;
                    } else {
                        let light = "-light"
                        let original_span_id = next_span[3]
                        if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (original_span_id in this.hits_data[[this.current_hit - 1]].annotations[this.id_to_category[next_span[0]]])) {
                            light = ""
                        }
                        sentence_html += `<span @mouseover.stop @mouseout.stop @click.stop @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${next_category} border-${next_category}${light} pointer span original_span ${outside}" data-category="${next_category}" data-id="${next_category}-` + next_span[3] + `">`;
                    }
                    i++;
                    if (i < original_spans.length - 1 && original_spans[i + 1][1] <= original_spans[i][2]) {
                        whether_more_overlap = true
                        // the next span is in the current span
                        let next_next_span = original_spans[i + 1]
                        sentence_html += original_sentence.substring(original_spans[i][1], next_next_span[1]);  
                        let next_category = this.id_to_category[next_next_span[0]]
                        if (next_next_span[1] == start && next_next_span[2] == end) {
                            sentence_html += `<span @mouseover.stop @mouseout.stop class="bg-${next_category}-light span">`;
                        } else {
                            let light = "-light"
                            let original_span_id = next_next_span[3]
                            if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (original_span_id in this.hits_data[[this.current_hit - 1]].annotations[this.id_to_category[next_next_span[0]]])) {
                                light = ""
                            }
                            sentence_html += `<span @mouseover.stop @mouseout.stop @click.stop @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${next_category} border-${next_category}${light} pointer span original_span" data-category="${next_category}" data-id="${next_category}-` + next_next_span[3] + `">`;
                        }
                        sentence_html += original_sentence.substring(next_next_span[1], next_next_span[2]);
                        sentence_html += "</span>";
                        sentence_html += original_sentence.substring(next_next_span[2], original_spans[i][2]);
                        console.log(original_sentence.substring(next_next_span[2], original_spans[i][2]))
                        sentence_html += `</span>`;
                        i++;
                    } else {
                        sentence_html += original_sentence.substring(next_span[1], next_span[2]);
                        sentence_html += "</span>";
                    }
                }
                if (start_i != i) {
                    if (whether_more_overlap) {
                        sentence_html += original_sentence.substring(original_spans[i - 1][2], original_spans[start_i][2]);
                    } else {
                        sentence_html += original_sentence.substring(original_spans[i][2], original_spans[start_i][2]);
                    }
                    sentence_html += `</span>`;
                    prev_idx = original_spans[start_i][2];
                } else {
                    sentence_html += original_sentence.substring(original_spans[i][1], original_spans[i][2]);
                    sentence_html += `</span>`;
                    prev_idx = original_spans[i][2];
                }
            }
            sentence_html += original_sentence.substring(prev_idx);
            this.original_html = sentence_html;
        },
        process_simplified_html() {
            let prev_idx = 0
            let sentence_html = ''
            let simplified_sentence = this.hits_data[this.current_hit - 1].simplified
            let simplified_spans = this.hits_data[this.current_hit - 1].simplified_spans
            simplified_spans.sort(function(a, b) {
                return a[1] - b[1] || b[2] - a[2];
            });
            // iterate simplified_spans list
            for (let i = 0; i < simplified_spans.length; i++) {
                sentence_html += simplified_sentence.substring(prev_idx, simplified_spans[i][1]);
                let category = this.id_to_category[simplified_spans[i][0]]
                let light = "-light"
                let simplified_span_id = simplified_spans[i][3]
                if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (simplified_span_id in this.hits_data[[this.current_hit - 1]].annotations[category])) {
                    light = ""
                }
                let outside = ""
                if (i < simplified_spans.length - 1 && simplified_spans[i + 1][1] <= simplified_spans[i][2]) {
                    outside = "outside"
                }
                if (category == "split" && (simplified_sentence.substring(simplified_spans[i][1], simplified_spans[i][2]) =="||")) {
                    sentence_html += `<span @mousedown.stop @mouseup.stop  @click="click_span"  @mouseover="hover_span" @mouseout="un_hover_span" class="${category} pointer span simplified_span txt-split${light} split-sign ${outside}" data-category="${category}" data-id="${category}-` + simplified_spans[i][3] + `">`;
                } else {
                    if (category == "split" || category == "structure") {
                        let childcategory = this.id_to_category[simplified_spans[i][4]]
                        let childid = simplified_spans[i][5]
                        sentence_html += `<span @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${category} border-${category}${light} pointer span simplified_span ${outside}" data-category="${category}" data-id="${category}-` + simplified_spans[i][3] + `" data-childcategory=${childcategory} data-childid=${childid}>`;
                    } else {
                        sentence_html += `<span @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${category} border-${category}${light} pointer span simplified_span ${outside}" data-category="${category}" data-id="${category}-` + simplified_spans[i][3] + `">`;
                    }
                }
                let start_i = i
                let whether_more_overlap = false
                while (i < simplified_spans.length - 1 && simplified_spans[i + 1][1] <= simplified_spans[start_i][2]) {
                    // the next span is in the current span
                    let next_span = simplified_spans[i + 1]
                    if (i == start_i) {
                        sentence_html += simplified_sentence.substring(simplified_spans[i][1], next_span[1]);
                    } else {
                        if (whether_more_overlap) {
                            sentence_html += simplified_sentence.substring(simplified_spans[i - 1][2], next_span[1]);
                        } else {
                            sentence_html += simplified_sentence.substring(simplified_spans[i][2], next_span[1]);
                        }
                    }
                    whether_more_overlap = false                 
                    let next_category = this.id_to_category[next_span[0]]
                    let outside = ""
                    if (i < simplified_spans.length - 2 && simplified_spans[i + 2][1] <= simplified_spans[i+1][2]) {
                        outside = "middleside"
                    }
                    if (next_category == "split" && (simplified_sentence.substring(next_span[1], next_span[2]) =="||")) {
                        sentence_html += `<span @mouseover.stop @mouseout.stop @click.stop @click="click_span"  @mouseover="hover_span" @mouseout="un_hover_span" class="${next_category} pointer span simplified_span txt-split split-sign" data-category="${next_category}" data-id="${next_category}-` + next_span[3] + `">`;
                    } else {
                        let light = "-light"
                        let simplified_span_id = next_span[3]
                        if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (simplified_span_id in this.hits_data[[this.current_hit - 1]].annotations[next_category])) {
                            light = ""
                        }
                        if (next_category == "split" || next_category == "structure") {
                            let childcategory = this.id_to_category[next_span[4]]
                            let childid = next_span[5]
                            sentence_html += `<span @mouseover.stop @mouseout.stop @click.stop @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${next_category} border-${next_category}${light} pointer span simplified_span ${outside}" data-category="${next_category}" data-id="${next_category}-` + next_span[3] + `"data-childcategory=${childcategory} data-childid=${childid}>`;
                        } else {
                            sentence_html += `<span @mouseover.stop @mouseout.stop @click.stop @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${next_category} border-${next_category}${light} pointer span simplified_span ${outside}" data-category="${next_category}" data-id="${next_category}-` + next_span[3] + `">`;
                        }
                    }
                    i++;
                    if (i < simplified_spans.length - 1 && simplified_spans[i + 1][1] <= simplified_spans[i][2]) {
                        whether_more_overlap = true
                        // the next span is in the current span
                        let next_next_span = simplified_spans[i + 1]
                        sentence_html += simplified_sentence.substring(simplified_spans[i][1], next_next_span[1]);  
                        let next_category = this.id_to_category[next_next_span[0]]
                        if (next_category == "split" && (simplified_sentence.substring(next_next_span[1], next_next_span[2]) =="||")) {
                            sentence_html += `<span @mouseover.stop @mouseout.stop @click.stop @click="click_span"  @mouseover="hover_span" @mouseout="un_hover_span" class="${next_category} pointer span simplified_span txt-split split-sign" data-category="${next_category}" data-id="${next_category}-` + next_next_span[3] + `">`;
                        } else {
                            let light = "-light"
                            let simplified_span_id = next_next_span[3]
                            if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (simplified_span_id in this.hits_data[[this.current_hit - 1]].annotations[next_category])) {
                                light = ""
                            }
                            if (next_category == "split" || next_category == "structure") {
                                let childcategory = this.id_to_category[next_next_span[4]]
                                let childid = next_next_span[5]
                                sentence_html += `<span @mouseover.stop @mouseout.stop @click.stop @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${next_category} border-${next_category}${light} pointer span simplified_span" data-category="${next_category}" data-id="${next_category}-` + next_next_span[3] + `"data-childcategory=${childcategory} data-childid=${childid}>`;
                            } else {
                                sentence_html += `<span @mouseover.stop @mouseout.stop @click.stop @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${next_category} border-${next_category}${light} pointer span simplified_span" data-category="${next_category}" data-id="${next_category}-` + next_next_span[3] + `">`;
                            }
                        }
                        sentence_html += simplified_sentence.substring(next_next_span[1], next_next_span[2]);
                        sentence_html += "</span>";
                        sentence_html += simplified_sentence.substring(next_next_span[2], simplified_spans[i][2]);
                        console.log(simplified_sentence.substring(next_next_span[2], simplified_spans[i][2]))
                        sentence_html += `</span>`;
                        i++;
                    } else {
                        sentence_html += simplified_sentence.substring(next_span[1], next_span[2]);
                        sentence_html += "</span>";
                    }
                }
                if (start_i != i) {
                    if (whether_more_overlap) {
                        sentence_html += simplified_sentence.substring(simplified_spans[i - 1][2], simplified_spans[start_i][2]);
                    } else {
                        sentence_html += simplified_sentence.substring(simplified_spans[i][2], simplified_spans[start_i][2]);
                    }
                    sentence_html += `</span>`;
                    prev_idx = simplified_spans[start_i][2];
                } else {
                    sentence_html += simplified_sentence.substring(simplified_spans[i][1], simplified_spans[i][2]);
                    sentence_html += `</span>`;
                    prev_idx = simplified_spans[i][2];
                }
            }
            sentence_html += simplified_sentence.substring(prev_idx);
            this.simplified_html = sentence_html;
        },
        process_simplified_html_with_selected_span(category, start, end) {
            this.selected_span_in_simplified_indexs = [start, end]
            let prev_idx = 0
            let sentence_html = ''
            let simplified_sentence = this.hits_data[this.current_hit - 1].simplified
            let simplified_spans = JSON.parse(JSON.stringify(this.hits_data[this.current_hit - 1].simplified_spans))
            let category_id = this.category_to_id[category]
            simplified_spans.push([category_id, start, end]);
            // rank simplified_spans list by [1]
            simplified_spans.sort(function(a, b) {
                return a[1] - b[1] || b[2] - a[2];
            });
            // iterate simplified_spans list
            for (let i = 0; i < simplified_spans.length; i++) {
                sentence_html += simplified_sentence.substring(prev_idx, simplified_spans[i][1]);
                let category = this.id_to_category[simplified_spans[i][0]]
                let outside = ""
                if (i < simplified_spans.length - 1 && simplified_spans[i + 1][1] <= simplified_spans[i][2]) {
                    outside = "outside"
                }
                if (simplified_spans[i][1] == start && simplified_spans[i][2] == end) {
                    sentence_html += `<span @mouseover.stop @mouseout.stop class="bg-${category}-light span ${outside}">`;
                } else {
                    if (category == "split" && (simplified_sentence.substring(simplified_spans[i][1], simplified_spans[i][2]) =="||")) {
                        sentence_html += `<span @mousedown.stop @mouseup.stop @click="click_span"  @mouseover="hover_span" @mouseout="un_hover_span" class="${category} pointer span simplified_span txt-split split-sign ${outside}" data-category="${category}" data-id="${category}-` + simplified_spans[i][3] + `">`;
                    } else {
                        sentence_html += `<span @mousedown.stop @mouseup.stop @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${category} border-${category} pointer span simplified_span ${outside}" data-category="${category}" data-id="${category}-` + simplified_spans[i][3] + `">`;
                    }
                }
                let start_i = i
                let whether_more_overlap = false
                while (i < simplified_spans.length - 1 && simplified_spans[i + 1][1] <= simplified_spans[start_i][2]) {
                    // the next span is in the current span
                    let next_span = simplified_spans[i + 1]
                    if (i == start_i) {
                        sentence_html += simplified_sentence.substring(simplified_spans[i][1], next_span[1]);
                    } else {
                        if (whether_more_overlap) {
                            sentence_html += simplified_sentence.substring(simplified_spans[i - 1][2], next_span[1]);
                        } else {
                            sentence_html += simplified_sentence.substring(simplified_spans[i][2], next_span[1]);
                        }
                    }                  
                    whether_more_overlap = false  
                    let next_category = this.id_to_category[next_span[0]]
                    let outside = ""
                    if (i < simplified_spans.length - 2 && simplified_spans[i + 2][1] <= simplified_spans[i+1][2]) {
                        outside = "middleside"
                    }
                    if (next_span[1] == start && next_span[2] == end) {
                        sentence_html += `<span @mouseover.stop @mouseout.stop class="bg-${next_category}-light span ${outside}">`;
                    } else {
                        if (next_category == "split" && (simplified_sentence.substring(next_span[1], next_span[2]) =="||")) {
                            sentence_html += `<span @mouseover.stop @mouseout.stop @click.stop @click="click_span"  @mouseover="hover_span" @mouseout="un_hover_span" class="${next_category} pointer span simplified_span txt-split split-sign" data-category="${next_category}" data-id="${next_category}-` + next_span[3] + `">`;
                        } else {
                            let light = "-light"
                            let simplified_span_id = next_span[3]
                            if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (simplified_span_id in this.hits_data[[this.current_hit - 1]].annotations[next_category])) {
                                light = ""
                            }
                            sentence_html += `<span @mouseover.stop @mouseout.stop @click.stop @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${next_category} border-${next_category}${light} pointer span simplified_span ${outside}" data-category="${next_category}" data-id="${next_category}-` + next_span[3] + `">`;
                        }
                    }
                    i++;
                    if (i < simplified_spans.length - 1 && simplified_spans[i + 1][1] <= simplified_spans[i][2]) {
                        whether_more_overlap = true
                        // the next span is in the current span
                        let next_next_span = simplified_spans[i + 1]
                        sentence_html += simplified_sentence.substring(simplified_spans[i][1], next_next_span[1]);  
                        let next_category = this.id_to_category[next_next_span[0]]
                        if (next_next_span[1] == start && next_next_span[2] == end) {
                            sentence_html += `<span @mouseover.stop @mouseout.stop class="bg-${next_category}-light span">`;
                        } else {
                            if (next_category == "split" && (simplified_sentence.substring(next_next_span[1], next_next_span[2]) =="||")) {
                                sentence_html += `<span @mouseover.stop @mouseout.stop @click.stop @click="click_span"  @mouseover="hover_span" @mouseout="un_hover_span" class="${next_category} pointer span simplified_span txt-split split-sign" data-category="${next_category}" data-id="${next_category}-` + next_next_span[3] + `">`;
                            } else {
                                let light = "-light"
                                let simplified_span_id = next_next_span[3]
                                if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (simplified_span_id in this.hits_data[[this.current_hit - 1]].annotations[next_category])) {
                                    light = ""
                                }
                                sentence_html += `<span @mouseover.stop @mouseout.stop @click.stop @click="click_span" @mouseover="hover_span" @mouseout="un_hover_span" class="${next_category} border-${next_category}${light} pointer span simplified_span" data-category="${next_category}" data-id="${next_category}-` + next_next_span[3] + `">`;
                            }
                        }
                        sentence_html += simplified_sentence.substring(next_next_span[1], next_next_span[2]);
                        sentence_html += "</span>";
                        sentence_html += simplified_sentence.substring(next_next_span[2], simplified_spans[i][2]);
                        console.log(simplified_sentence.substring(next_next_span[2], simplified_spans[i][2]))
                        sentence_html += `</span>`;
                        i++;
                    } else {
                        sentence_html += simplified_sentence.substring(next_span[1], next_span[2]);
                        sentence_html += "</span>";
                    }
                }
                if (start_i != i) {
                    if (whether_more_overlap) {
                        sentence_html += simplified_sentence.substring(simplified_spans[i - 1][2], simplified_spans[start_i][2]);
                    } else {
                        sentence_html += simplified_sentence.substring(simplified_spans[i][2], simplified_spans[start_i][2]);
                    }
                    sentence_html += `</span>`;
                    prev_idx = simplified_spans[start_i][2];
                } else {
                    sentence_html += simplified_sentence.substring(simplified_spans[i][1], simplified_spans[i][2]);
                    sentence_html += `</span>`;
                    prev_idx = simplified_spans[i][2];
                }
            }
            sentence_html += simplified_sentence.substring(prev_idx);
            this.simplified_html = sentence_html;
        },
        process_edits_html() {
            this.edits_dict = {'deletion': {}, 'substitution': {}, 'insertion': {}, 'split':{}, 'reorder':{}, 'structure':{}}
            let original_spans = this.hits_data[this.current_hit - 1].original_spans
            let simplified_spans = this.hits_data[this.current_hit - 1].simplified_spans
            // map for substituion that mapping to simplified span
            let substitution_map = {}

            let spans_for_sort = [...original_spans]
            // remove split and structure span from spans_for_sort
            for (let i = 0; i < spans_for_sort.length; i++) {
                if (spans_for_sort[i][0] == 2 || spans_for_sort[i][0] == 5) {
                    spans_for_sort.splice(i, 1);
                    i--;
                }
            }
            let structure_in_ids = []
            let new_html = ''
            for (let i = 0; i < original_spans.length; i++) {
                if (original_spans[i][0] == 0) {
                    this.edits_dict['deletion'][original_spans[i][3]] = original_spans[i];
                } else if (original_spans[i][0] == 1) {
                    this.edits_dict['substitution'][original_spans[i][3]] = [original_spans[i]];
                } else if (original_spans[i][0] == 2) {
                    if (!(original_spans[i][3] in this.edits_dict['split'])) {
                        this.edits_dict['split'][original_spans[i][3]] = {'split':null, 'deletion': {}, 'insertion': {}, 'substitution': {}, 'reorder':{}};
                    }
                    let associated_span_category = this.id_to_category[original_spans[i][4]]
                    if (associated_span_category == 'reorder' || associated_span_category == 'substitution') {
                        this.edits_dict['split'][original_spans[i][3]][associated_span_category][original_spans[i][5]] = [original_spans[i]];
                    } else {
                        this.edits_dict['split'][original_spans[i][3]][associated_span_category][original_spans[i][5]] = original_spans[i];
                    }
                } else if (original_spans[i][0] == 4) {
                    this.edits_dict['reorder'][original_spans[i][3]] = [original_spans[i]];
                } else if (original_spans[i][0] == 5) {
                    if (!(structure_in_ids.includes(original_spans[i][3]))) {
                        spans_for_sort.push(original_spans[i]);
                        structure_in_ids.push(original_spans[i][3]);
                        this.edits_dict['structure'][original_spans[i][3]] = {'deletion': {}, 'insertion': {}, 'substitution': {}, 'reorder':{}};
                    }
                    let associated_span_category = this.id_to_category[original_spans[i][4]]
                    if (associated_span_category == 'reorder' || associated_span_category == 'substitution') {
                        this.edits_dict['structure'][original_spans[i][3]][associated_span_category][original_spans[i][5]] = [original_spans[i]];
                    } else {
                        this.edits_dict['structure'][original_spans[i][3]][associated_span_category][original_spans[i][5]] = original_spans[i];
                    }
                }
            }
            for (let i = 0; i < simplified_spans.length; i++) {
                if (simplified_spans[i][0] == 2) {
                    if (!(simplified_spans[i][3] in this.edits_dict['split'])) {
                        this.edits_dict['split'][simplified_spans[i][3]] = {'split':null, 'deletion': {}, 'insertion': {}, 'substitution': {}, 'reorder':{}};
                    }
                    if (this.hits_data[this.current_hit - 1].simplified.substring(simplified_spans[i][1], simplified_spans[i][2]) == "||") {
                        // push at the front
                        this.edits_dict['split'][simplified_spans[i][3]]["split"] = simplified_spans[i];
                        spans_for_sort.push(simplified_spans[i]);
                    } else {
                        let associated_span_category = this.id_to_category[simplified_spans[i][4]]
                        if (associated_span_category == 'reorder' || associated_span_category == 'substitution') {
                            this.edits_dict['split'][simplified_spans[i][3]][associated_span_category][simplified_spans[i][5]].push(simplified_spans[i]);
                        } else {
                            this.edits_dict['split'][simplified_spans[i][3]][associated_span_category][simplified_spans[i][5]] = simplified_spans[i];
                        }
                    }
                } else if (simplified_spans[i][0] == 3) {
                    this.edits_dict['insertion'][simplified_spans[i][3]] = simplified_spans[i];
                    spans_for_sort.push(simplified_spans[i]);
                } else if (simplified_spans[i][0] == 1) {
                    this.edits_dict['substitution'][simplified_spans[i][3]].push(simplified_spans[i]);
                    substitution_map[simplified_spans[i][3]] = simplified_spans[i];
                } else if (simplified_spans[i][0] == 4) {
                    this.edits_dict['reorder'][simplified_spans[i][3]].push(simplified_spans[i]);
                } else if (simplified_spans[i][0] == 5) {
                    if (!(simplified_spans[i][3] in this.edits_dict['structure'])) {
                        this.edits_dict['structure'][simplified_spans[i][3]] = {'deletion': {}, 'insertion': {}, 'substitution': {}, 'reorder':{}};
                    }
                    if (!(structure_in_ids.includes(simplified_spans[i][3]))) {
                        spans_for_sort.push(simplified_spans[i]);
                        structure_in_ids.push(simplified_spans[i][3]);
                    }
                    let associated_span_category = this.id_to_category[simplified_spans[i][4]]
                    if (associated_span_category == 'reorder' || associated_span_category == 'substitution') {
                        console.log(this.edits_dict['structure'])
                        this.edits_dict['structure'][simplified_spans[i][3]][associated_span_category][simplified_spans[i][5]].push(simplified_spans[i]);
                    } else {
                        this.edits_dict['structure'][simplified_spans[i][3]][associated_span_category][simplified_spans[i][5]] = simplified_spans[i];
                    }
                }
            }

            spans_for_sort.sort(function(a, b) {
                return a[1] - b[1];
            });

            for (let span of spans_for_sort) {
                let i = span[3]
                let key_id = span[0];
                let key = this.id_to_category[key_id];
                let key_short = this.key_to_key_short[key];
                let light = "-light"
                if (("annotations" in this.hits_data[[this.current_hit - 1]]) && (i in this.hits_data[[this.current_hit - 1]].annotations[key])) {
                    light = ""
                }
                new_html += `<div class='cf'>`
                new_html += `<div class="fl w-80 mb4 edit">`;
                new_html += `<span @mouseover="hover_span" @mouseout="un_hover_span" data-id="${key}-${i}" data-category="${key}" class="default_cursor">`
                new_html += `<span class="edit-type txt-${key}${light} f3">${key_short} </span>`;
                new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                if (key == 'deletion') {
                    new_html += `&nbsp${this.hits_data[this.current_hit - 1].original.substring(span[1],span[2])}&nbsp`;
                    new_html += `</span>`;
                } else if (key == 'reorder') {
                    new_html += `&nbsp${this.hits_data[this.current_hit - 1].original.substring(span[1], span[2])}&nbsp`;
                    new_html += `</span>`;
                } else if (key == "substitution") {
                    new_html += `&nbsp${this.hits_data[this.current_hit - 1].original.substring(span[1], span[2])}&nbsp`;
                    new_html += `</span>`;
                    new_html += `<span class="edit-type txt-${key}${light} f3"> with </span>`;
                    new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                    new_html += `&nbsp${this.hits_data[this.current_hit - 1].simplified.substring(substitution_map[i][1], substitution_map[i][2])}&nbsp`;
                    new_html += `</span>`;
                } else if (key == "split") {
                    // console.log(span)
                    new_html += `&nbsp${this.hits_data[this.current_hit - 1].simplified.substring(span[1], span[2])}&nbsp</span>`;
                    let first_span = 0
                    for (let current_category in this.edits_dict[key][i]) {
                        if (current_category == "split") {
                            continue;
                        }
                        let current_category_short = this.key_to_key_short[current_category];
                        for (let j in this.edits_dict[key][i][current_category]) {
                            if (first_span == 0) {
                                new_html += `<span class="edit-type txt-${key}${light} f3"> (</span>`;
                                first_span = 1;
                            } else {
                                new_html += `<span class="edit-type txt-${key}${light} f3"> , </span>`;
                            }
                            if (current_category == "insertion") {
                                new_html += `<span class="edit-type txt-${key}${light} f3"> ${current_category_short} </span>`;
                                new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                                new_html += `&nbsp${this.hits_data[this.current_hit - 1].simplified.substring(this.edits_dict[key][i][current_category][j][1], this.edits_dict[key][i][current_category][j][2])}&nbsp`;
                                new_html += `</span>`;
                            } else if (current_category == "deletion") {
                                new_html += `<span class="edit-type txt-${key}${light} f3"> ${current_category_short} </span>`;
                                new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                                new_html += `&nbsp${this.hits_data[this.current_hit - 1].original.substring(this.edits_dict[key][i][current_category][j][1], this.edits_dict[key][i][current_category][j][2])}&nbsp`;
                                new_html += `</span>`;
                            } else if (current_category == "substitution") {
                                new_html += `<span class="edit-type txt-${key}${light} f3"> ${current_category_short} </span>`;
                                new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                                new_html += `&nbsp${this.hits_data[this.current_hit - 1].original.substring(this.edits_dict[key][i][current_category][j][0][1], this.edits_dict[key][i][current_category][j][0][2])}&nbsp`;
                                new_html += `</span>`;
                                new_html += `<span class="edit-type txt-${key}${light} f3"> with </span>`;
                                new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                                new_html += `&nbsp${this.hits_data[this.current_hit - 1].simplified.substring(this.edits_dict[key][i][current_category][j][1][1], this.edits_dict[key][i][current_category][j][1][2])}&nbsp`;
                                new_html += `</span>`;
                            } else if (current_category == "reorder") {
                                new_html += `<span class="edit-type txt-${key}${light} f3"> ${current_category_short} </span>`;
                                new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                                new_html += `&nbsp${this.hits_data[this.current_hit - 1].original.substring(this.edits_dict[key][i][current_category][j][0][1], this.edits_dict[key][i][current_category][j][0][2])}&nbsp`;
                                new_html += `</span>`;
                            }
                        }
                    }
                    if (first_span == 1) {
                        new_html += `<span class="edit-type txt-${key}${light} f3"> )</span>`;
                    }
                } else if (key == "structure") {
                    // console.log(span)
                    new_html += `&nbsp<i class="fa-solid fa-tree"></i>&nbsp</span>`;
                    let first_span = 0
                    for (let current_category in this.edits_dict[key][i]) {
                        let current_category_short = this.key_to_key_short[current_category];
                        for (let j in this.edits_dict[key][i][current_category]) {
                            if (first_span == 0) {
                                new_html += `<span class="edit-type txt-${key}${light} f3"> (</span>`;
                                first_span = 1;
                            } else {
                                new_html += `<span class="edit-type txt-${key}${light} f3"> , </span>`;
                            }
                            if (current_category == "insertion") {
                                new_html += `<span class="edit-type txt-${key}${light} f3"> ${current_category_short} </span>`;
                                new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                                new_html += `&nbsp${this.hits_data[this.current_hit - 1].simplified.substring(this.edits_dict[key][i][current_category][j][1], this.edits_dict[key][i][current_category][j][2])}&nbsp`;
                                new_html += `</span>`;
                            } else if (current_category == "deletion") {
                                new_html += `<span class="edit-type txt-${key}${light} f3"> ${current_category_short} </span>`;
                                new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                                new_html += `&nbsp${this.hits_data[this.current_hit - 1].original.substring(this.edits_dict[key][i][current_category][j][1], this.edits_dict[key][i][current_category][j][2])}&nbsp`;
                                new_html += `</span>`;
                            } else if (current_category == "substitution") {
                                new_html += `<span class="edit-type txt-${key}${light} f3"> ${current_category_short} </span>`;
                                new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                                new_html += `&nbsp${this.hits_data[this.current_hit - 1].original.substring(this.edits_dict[key][i][current_category][j][0][1], this.edits_dict[key][i][current_category][j][0][2])}&nbsp`;
                                new_html += `</span>`;
                                new_html += `<span class="edit-type txt-${key}${light} f3"> with </span>`;
                                new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                                new_html += `&nbsp${this.hits_data[this.current_hit - 1].simplified.substring(this.edits_dict[key][i][current_category][j][1][1], this.edits_dict[key][i][current_category][j][1][2])}&nbsp`;
                                new_html += `</span>`;
                            } else if (current_category == "reorder") {
                                new_html += `<span class="edit-type txt-${key}${light} f3"> ${current_category_short} </span>`;
                                new_html += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${i}" data-category="${key}">`;
                                new_html += `&nbsp${this.hits_data[this.current_hit - 1].original.substring(this.edits_dict[key][i][current_category][j][0][1], this.edits_dict[key][i][current_category][j][0][2])}&nbsp`;
                                new_html += `</span>`;
                            }
                        }
                    }
                    if (first_span == 1) {
                        new_html += `<span class="edit-type txt-${key}${light} f3"> )</span>`;
                    }
                } else {
                    new_html += `&nbsp${this.hits_data[this.current_hit - 1].simplified.substring(span[1], span[2])}&nbsp</span>`;
                }
                
                new_html += ` : `;

                if (!(i in this.hits_data[this.current_hit - 1].annotations[key])) {
                    new_html += `<span class="f4 i black-60">this edit is not annotated yet, click <i class="fa-solid fa-pencil"></i> to start!</span>`;
                } else {
                    let annotation = this.hits_data[this.current_hit - 1].annotations[key][i];
                    let annotation_text = ""
                    if (key == 'deletion') {
                        if (annotation[0] == "perfect" ||  annotation[0] == "good") {
                            annotation_text = `<span class="light-orange ba bw1 pa1">${annotation[0]} deletion</span>`
                        } else {
                            annotation_text = `<span class="light-purple ba bw1 pa1">${annotation[0]} deletion</span>`;
                        }
                        if (annotation[1] == "yes") {
                            annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                        }
                        if (annotation[2] == "yes") {
                            annotation_text += ` <span class="brown ba bw1 pa1 br-pills">Coref error</span>`;
                        }
                    } else if (key == 'substitution') {
                        let type = annotation[0]
                        if (type == "same") {
                            if (annotation[1] == "positive") {
                                annotation_text += `<span class="light-orange ba bw1 pa1">good paraphrase</span>`;
                                annotation_text += `<span class="light-pink br-pills ba bw1 pa1">efficacy: ${annotation[2]}</span>`;
                            } else if (annotation[1] == "negative") {
                                annotation_text += `<span class="light-purple ba bw1 pa1">bad paraphrase</span>`;
                                annotation_text += `<span class="light-pink br-pills ba bw1 pa1">severity: ${annotation[3]}</span>`;
                            } else {
                                annotation_text += `<span class="light-purple ba bw1 pa1">unnecessary paraphrase</span>`;
                            }
                            if (annotation[4] == "yes") {
                                annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                            }
                        } else if (type == "different") {
                            annotation_text += `<span class="light-purple ba bw1 pa1">bad substitution that changes the meaning</span>`;
                            annotation_text += `<span class="light-pink ba bw1 pa1">severity: ${annotation[1]}</span>`;
                            if (annotation[2] == "yes") {
                                annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                            }
                        } else if (type == "less") {
                            if (annotation[1] == "perfect" ||  annotation[1] == "good") {
                                annotation_text = `<span class="light-orange ba bw1 pa1">${annotation[1]} substitution that removes unnecessary information</span>`
                            } else {
                                annotation_text = `<span class="light-purple ba bw1 pa1">${annotation[1]} substitution that removes necessary information</span>`;
                            }
                            if (annotation[2] == "yes") {
                                annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                            }
                            if (annotation[3] == "yes") {
                                annotation_text += ` <span class="brown ba bw1 pa1 br-pills">Coref error</span>`;
                            }
                        } else if (type == "more") {
                            if (annotation[1] == "elaboration") {
                                annotation_text += `<span class="light-orange ba bw1 pa1">good substitution with elaboration</span>`;
                                annotation_text += `<span class="light-pink ba bw1 pa1">efficacy: ${annotation[2]}</span>`;
                                if (annotation[3] == "yes") {
                                    annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                                }
                            } else if (annotation[1] == "hallucination") {
                                if (annotation[2] == "no") {
                                    annotation_text += `<span class="light-purple ba bw1 pa1">bad substitution with <i>irrelevant</i> hallucination</span>`;
                                } else {
                                    annotation_text += `<span class="light-purple ba bw1 pa1">bad substitution with <i>relevant</i> hallucination</span>`;
                                }
                                annotation_text += `<span class="light-pink ba bw1 pa1">severity: ${annotation[3]}</span>`;
                                if (annotation[4] == "yes") {
                                    annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                                }
                            } else if (annotation[1] == "trivial") {
                                if (annotation[2] == "no") {
                                    annotation_text += `<span class="light-purple ba bw1 pa1">unnecessary substitution with trivial change</span>`;
                                } else {
                                    annotation_text += `<span class="light-orange ba bw1 pa1">good substitution with trivial change</span>`;
                                    annotation_text += `<span class="light-pink ba bw1 pa1">efficacy: ${annotation[3]}</span>`;
                                }
                                if (annotation[4] == "yes") {
                                    annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                                }
                            } else if (annotation[1] == "repetition") {
                                annotation_text += `<span class="light-purple ba bw1 pa1">bad substitution with repetition</span>`;
                                annotation_text += `<span class="light-pink ba bw1 pa1">severity: ${annotation[2]}</span>`;
                                if (annotation[3] == "yes") {
                                    annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                                }
                            } else if (annotation[1] == "contradiction") {
                                annotation_text += `<span class="light-purple ba bw1 pa1">bad substitution with contradiction</span>`;
                                annotation_text += `<span class="light-pink ba bw1 pa1">severity: ${annotation[2]}</span>`;
                                if (annotation[3] == "yes") {
                                    annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                                }
                            }
                        }
                    } else if (key == 'insertion') {
                        if (annotation[0] == "elaboration") {
                            annotation_text += `<span class="light-orange ba bw1 pa1">good substitution with elaboration</span>`;
                            annotation_text += `<span class="light-pink ba bw1 pa1">efficacy: ${annotation[1]}</span>`;
                            if (annotation[2] == "yes") {
                                annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                            }
                        } else if (annotation[0] == "hallucination") {
                            if (annotation[1] == "no") {
                                annotation_text += `<span class="light-purple ba bw1 pa1">bad substitution with <i>irrelevant</i> hallucination</span>`;
                            } else {
                                annotation_text += `<span class="light-purple ba bw1 pa1">bad substitution with <i>relevant</i> hallucination</span>`;
                            }
                            annotation_text += `<span class="light-pink ba bw1 pa1">severity: ${annotation[2]}</span>`;
                            if (annotation[3] == "yes") {
                                annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                            }
                        } else if (annotation[0] == "trivial") {
                            if (annotation[1] == "no") {
                                annotation_text += `<span class="light-purple ba bw1 pa1">unnecessary substitution with trivial change</span>`;
                            } else {
                                annotation_text += `<span class="light-orange ba bw1 pa1">good substitution with trivial change</span>`;
                                annotation_text += `<span class="light-pink ba bw1 pa1">efficacy: ${annotation[2]}</span>`;
                            }
                            if (annotation[3] == "yes") {
                                annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                            }
                        } else if (annotation[0] == "repetition") {
                            annotation_text += `<span class="light-purple ba bw1 pa1">bad substitution with repetition</span>`;
                            annotation_text += `<span class="light-pink ba bw1 pa1">severity: ${annotation[1]}</span>`;
                            if (annotation[2] == "yes") {
                                annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                            }
                        } else if (annotation[0] == "contradiction") {
                            annotation_text += `<span class="light-purple ba bw1 pa1">bad substitution with contradiction</span>`;
                            annotation_text += `<span class="light-pink ba bw1 pa1">severity: ${annotation[1]}</span>`;
                            if (annotation[2] == "yes") {
                                annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                            }
                        }
                    } else if (key == 'split') {
                        if (annotation[0] == "positive") {
                            annotation_text += `<span class="light-orange ba bw1 pa1">good split</span>`
                            annotation_text += `<span class="light-pink ba bw1 pa1">efficacy: ${annotation[2]}</span>`;
                        } else if (annotation[0] == "negative") {
                            annotation_text += `<span class="light-purple ba bw1 pa1">bad split</span>`
                            annotation_text += `<span class="light-pink ba bw1 pa1">severity: ${annotation[1]}</span>`;
                        } else {
                            annotation_text += `<span class="light-purple ba bw1 pa1">unnecessary split</span>`
                        }
                        if (annotation[3] == "yes") {
                            annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                        }
                    } else if (key == 'reorder') {
                        annotation_text += `<span class="black ba bw1 pa1">${annotation[4]}-level</span>`
                        if (annotation[0] == "positive") {
                            annotation_text += `<span class="light-orange ba bw1 pa1">good reorder</span>`
                            annotation_text += `<span class="light-pink ba bw1 pa1">efficacy: ${annotation[2]}</span>`;
                        } else if (annotation[0] == "negative") {
                            annotation_text += `<span class="light-purple ba bw1 pa1">bad reorder</span>`
                            annotation_text += `<span class="light-pink ba bw1 pa1">severity: ${annotation[1]}</span>`;
                        } else {
                            annotation_text += `<span class="light-purple ba bw1 pa1">unnecessary reorder</span>`
                        }
                        if (annotation[3] == "yes") {
                            annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                        }
                    } else if (key == 'structure') {
                        if (annotation[0] == "positive") {
                            annotation_text += `<span class="light-orange ba bw1 pa1">good structure change</span>`
                            annotation_text += `<span class="light-pink ba bw1 pa1">efficacy: ${annotation[2]}</span>`;
                        } else if (annotation[0] == "negative") {
                            annotation_text += `<span class="light-purple ba bw1 pa1">bad structure change</span>`
                            annotation_text += `<span class="light-pink ba bw1 pa1">severity: ${annotation[1]}</span>`;
                        } else {
                            annotation_text += `<span class="light-purple ba bw1 pa1">unnecessary structure change</span>`
                        }
                        if (annotation[3] == "yes") {
                            annotation_text += ` <span class="brown ba bw1 pa1 br-100">G</span>`;
                        }
                    }
                    new_html += `<span class="f4 i">${annotation_text}</span>`;
                }
                new_html += '</span>'
                new_html += `</div>`;
                new_html += `<div class="fl w-20 mb4 operation tc">`;
                new_html += `<i @click="annotate_edit" class="annotation-icon fa-solid fa-pencil mr3 pointer dim" data-id="${key}-${i}" data-category="${key}"></i>`;
                new_html += `<i @click="trash_edit" class="fa-solid fa-trash-can ml4 pointer dim" data-id="${key}-${i}" data-category="${key}"></i>`;
                new_html += `</div>`;
                new_html += `</div>`;
            }
            this.edits_html = new_html;
        },
        process_everything() {
            this.process_original_html();
            this.process_simplified_html();
            this.process_edits_html();
            $(`.circle`).removeClass('circle-active');
            $(`#circle-${this.current_hit}`).addClass('circle-active');
            if ("bookmark" in this.hits_data[this.current_hit - 1] && this.hits_data[this.current_hit - 1]["bookmark"]) {
                $(`.bookmark`).addClass('bookmark-active');
            } else {
                $(`.bookmark`).removeClass('bookmark-active');
            }
            if ("comment" in this.hits_data[this.current_hit - 1]) {
                $(`#comment_area`).val(this.hits_data[this.current_hit - 1]["comment"]);
            } else {
                $(`#comment_area`).val("");
            }
        },
        go_to_hit(hit_num) {
            if (hit_num > this.total_hits) {
                hit_num = this.total_hits;
            } else if (hit_num < 1) {
                hit_num = 1;
            }
            this.current_hit = hit_num;
            this.process_everything();
        },
        go_to_hit_circle(hit_num, event) {
            if (hit_num > this.total_hits) {
                hit_num = this.total_hits;
            } else if (hit_num < 1) {
                hit_num = 1;
            }
            this.current_hit = hit_num;

            this.process_everything();
        },
        add_an_edit(event) {
            if(this.open){
                $('#add_an_edit').hide(400);
                $(".icon-default").removeClass("open")
            } else{
                $('#add_an_edit').slideDown(400);
                $(".icon-default").addClass("open")
            }
            this.open = !this.open;
        },
        leave_comment(event) {
            // if #comment_area_div is not displayed, display it
            $("#comment_area_div").show();
        },
        record_comment(event) {
            // record the comment
            this.hits_data[this.current_hit - 1]["comment"] = event.target.value;
        },
        cancel_click() {
            $(".icon-default").removeClass("open")
            this.refresh_edit();
        },
        save_click() {
            $(".icon-default").removeClass("open")
            this.open = !this.open;
            let original_spans = this.hits_data[this.current_hit - 1].original_spans
            let simplified_spans = this.hits_data[this.current_hit - 1].simplified_spans
            let selected_category = $("input[name=edit_cotegory]:checked").val();
            let category_edits = this.edits_dict[selected_category]
            // get the highest key in the category_edits
            let max_key = 0;
            for (let key in category_edits) {
                if (parseInt(key) > max_key) {
                    max_key = parseInt(key);
                }
            }
            if (selected_category == "deletion") {
                let new_deletion = [0, this.selected_span_in_original_indexs[0], this.selected_span_in_original_indexs[1], max_key + 1]
                original_spans.push(new_deletion)
            } else if (selected_category == "substitution") {
                let new_substitution = [[1, this.selected_span_in_original_indexs[0], this.selected_span_in_original_indexs[1], max_key + 1], [1, this.selected_span_in_simplified_indexs[0], this.selected_span_in_simplified_indexs[1], max_key + 1]]
                original_spans.push(new_substitution[0])
                simplified_spans.push(new_substitution[1])
            } else if (selected_category == "reorder") {
                let new_reorder = [[4, this.selected_span_in_original_indexs[0], this.selected_span_in_original_indexs[1], max_key + 1], [4, this.selected_span_in_simplified_indexs[0], this.selected_span_in_simplified_indexs[1], max_key + 1]]
                original_spans.push(new_reorder[0])
                simplified_spans.push(new_reorder[1])
            } else if (selected_category == "split" || selected_category == "structure") {
                let selected_edits_key_map = {"deletion": {}, "substitution": {}, "reorder": {}, "insertion": {}}
                for (let temp_category in this.selected_edits) {
                    let j = 1;
                    for (let temp_id in this.selected_edits[temp_category]) {
                        selected_edits_key_map[temp_category][temp_id] = j;
                        j++;
                    }
                }
                let newspans = []
                for (let i = 0; i < original_spans.length; i++) {
                    let span = original_spans[i]
                    let span_category = this.id_to_category[span[0]]
                    let span_id = span[3]
                    if ((span_category in this.selected_edits) && (span[3] in this.selected_edits[span_category])) {
                        span.push(span[0])
                        span.push(selected_edits_key_map[span_category][span[3]])
                        span[0] = this.category_to_id[selected_category]
                        if (selected_category == "split") {
                            span[3] = this.selected_split_id
                        } else if (selected_category == "structure") {
                            span[3] = max_key + 1
                        }

                        if (span_id in this.hits_data[this.current_hit - 1]["annotations"][span_category]) {
                            delete this.hits_data[this.current_hit - 1]["annotations"][span_category][span_id]
                        }
                    }
                    newspans.push(span)
                }

                let newspans_simplified = []
                for (let i = 0; i < simplified_spans.length; i++) {
                    let span = simplified_spans[i]
                    let span_category = this.id_to_category[span[0]]
                    let span_id = span[3]
                    if ((span_category in this.selected_edits) && (span[3] in this.selected_edits[span_category])) {
                        span.push(span[0])
                        span.push(selected_edits_key_map[span_category][span[3]])
                        span[0] = this.category_to_id[selected_category]
                        if (selected_category == "split") {
                            span[3] = this.selected_split_id
                        } else if (selected_category == "structure") {
                            span[3] = max_key + 1
                        }

                        if (span_id in this.hits_data[this.current_hit - 1]["annotations"][span_category]) {
                            delete this.hits_data[this.current_hit - 1]["annotations"][span_category][span_id]
                        }
                    }
                    newspans_simplified.push(span)
                }
                this.hits_data[this.current_hit - 1].original_spans = newspans
                this.hits_data[this.current_hit - 1].simplified_spans = newspans_simplified
            } else if (selected_category == "insertion") {
                let new_insertion = [3, this.selected_span_in_simplified_indexs[0], this.selected_span_in_simplified_indexs[1], max_key + 1]
                simplified_spans.push(new_insertion)
            }
            this.process_everything();
            this.refresh_edit();
        },
        save_annotation_click(category, event) {
            let edit_id = this.annotating_edit_span_category_id
            
            let box = []
            if (category == "deletion") {
                box = [this.deletion_severity_box, this.deletion_grammar_yes_no_box, this.deletion_coref_yes_no_box]
            } else if (category == "insertion") {
                if (this.insertion_type_box == "elaboration") {
                    box = [this.insertion_type_box, this.insertion_elaboration_severity_box, this.insertion_grammar_yes_no_box]
                } else if (this.insertion_type_box == "hallucination") {
                    box = [this.insertion_type_box, this.insertion_hallucination_relevance_yes_no_box, this.insertion_hallucination_severity_box, this.insertion_grammar_yes_no_box]
                } else if (this.insertion_type_box == "trivial") {
                    box = [this.insertion_type_box, this.insertion_trivial_yes_no_box, this.insertion_trivial_severity_box, this.insertion_grammar_yes_no_box]
                } else if (this.insertion_type_box == "repetition") {
                    box = [this.insertion_type_box, this.insertion_repetition_severity_box, this.insertion_grammar_yes_no_box]
                } else if (this.insertion_type_box == "contradiction") {
                    box = [this.insertion_type_box, this.insertion_contradiction_severity_box, this.insertion_grammar_yes_no_box]
                }
            } else if (category == "substitution") {
                if (this.substitution_type_box == "same") {
                    box = [this.substitution_type_box, this.substitution_impact_box, this.substitution_positive_severity_box, this.substitution_negative_severity_box, this.substitution_grammar_yes_no_box]
                } else if (this.substitution_type_box == "different") {
                    box = [this.substitution_type_box, this.substitution_different_severity_box, this.substitution_grammar_yes_no_box]
                } else if (this.substitution_type_box == "less") {
                    box = [this.substitution_type_box, this.substitution_less_severity_box, this.substitution_grammar_yes_no_box, this.substitution_coref_yes_no_box]
                } else if (this.substitution_type_box == "more") {
                    if (this.substitution_more_type_box == "elaboration") {
                        box = [this.substitution_type_box, this.substitution_more_type_box, this.substitution_elaboration_severity_box, this.substitution_grammar_yes_no_box]
                    } else if (this.substitution_more_type_box == "hallucination") {
                        box = [this.substitution_type_box, this.substitution_more_type_box, this.substitution_hallucination_relevance_yes_no_box, this.substitution_hallucination_severity_box, this.substitution_grammar_yes_no_box]
                    } else if (this.substitution_more_type_box == "trivial") {
                        box = [this.substitution_type_box, this.substitution_more_type_box, this.substitution_trivial_yes_no_box, this.substitution_trivial_severity_box, this.substitution_grammar_yes_no_box]
                    } else if (this.substitution_more_type_box == "repetition") {
                        box = [this.substitution_type_box, this.substitution_more_type_box, this.substitution_repetition_severity_box, this.substitution_grammar_yes_no_box]
                    } else if (this.substitution_more_type_box == "contradiction") {
                        box = [this.substitution_type_box, this.substitution_more_type_box, this.substitution_contradiction_severity_box, this.substitution_grammar_yes_no_box]
                    }
                }
            } else if (category == "split") {
                box = [this.split_impact_box, this.split_negative_severity_box, this.split_positive_severity_box, this.split_grammar_yes_no_box]
            } else if (category == "reorder") {
                box = [this.reorder_impact_box, this.reorder_negative_severity_box, this.reorder_positive_severity_box, this.reorder_grammar_yes_no_box, this.reorder_level_box]
            } else if (category == "structure") {
                box = [this.structure_impact_box, this.structure_negative_severity_box, this.structure_positive_severity_box, this.structure_grammar_yes_no_box]
            }
            console.log(box)
            this.hits_data[this.current_hit - 1].annotations[category][edit_id] = box
            this.process_everything();
            this.refresh_edit();
        },
        substitution_type_click(event) {
            // get the value of the clicked button
            let value = event.target.value;
            // if $(`.substitution-${value}`) is not visible, show it
            if (!($(`.substitution-${value}`).is(":visible"))) {
                $(`.substitution-type-div`).hide(400);
                $(`.substitution-${value}`).slideDown(400);
                if (value != "more") {
                    $(`.substitution-more-div`).hide(400);
                } else {
                    if ($(`input[name='substitution-more-type']:checked`).val() != undefined) {
                        $(`.substitution-more-${$(`input[name='substitution-more-type']:checked`).val()}`).slideDown(400);
                    }
                }
                if (value != "same") {
                    $(`.substitution-impact-div`).hide(400);
                }
                if (value != "less") {
                    $(`.substitution-coref-div`).hide(400);
                }
            }
        },
        substitution_more_click(event) {
            // get the value of the clicked button
            let value = event.target.value;
            if (value != "trivial") {
                this.substitution_hide_trivial_efficacy()
            }
            // if $(`.substitution-${value}`) is not visible, show it
            if (!$(`.substitution-more-${value}`).is(":visible")) {
                $(`.substitution-more-div`).hide(400);
                $(`.substitution-more-${value}`).slideDown(400);
            }
        },
        substitution_show_grammar(event) {
            if ($(`.substitution-coref-div`).is(":visible")) {
                $('.substitution-coref-div').hide(400);
            }
            if (!$(`.substitution-grammar-div`).is(":visible")) {
                $('.substitution-grammar-div').slideDown(400);
            }
        },
        substitution_show_coref(event) {
            if (!$(`.substitution-coref-div`).is(":visible")) {
                $('.substitution-coref-div').slideDown(400);
            }
            if (!$(`.substitution-grammar-div`).is(":visible")) {
                $('.substitution-grammar-div').slideDown(400);
            }
        },
        substitution_show_trivial_efficacy(event) {
            if (!$(`.substitution-more-trivial-efficacy`).is(":visible")) {
                $('.substitution-more-trivial-efficacy').slideDown(400);
            }
        },
        substitution_hide_trivial_efficacy(event) {
            if ($(`.substitution-more-trivial-efficacy`).is(":visible")) {
                $('.substitution-more-trivial-efficacy').hide(400);
            }
            if (!$(`.substitution-grammar-div`).is(":visible")) {
                $('.substitution-grammar-div').slideDown(400);
            }
        },
        insertion_type_click(event) {
            let value = event.target.value;
            if (value != "trivial") {
                this.insertion_hide_trivial_efficacy()
            }
            if (!$(`.insertion-type-${value}`).is(":visible")) {
                $(`.insertion-type-div`).hide(400);
                $(`.insertion-type-${value}`).slideDown(400);
            }
        },
        insertion_show_grammar(event) {
            if (!$(`.insertion-grammar-div`).is(":visible")) {
                $('.insertion-grammar-div').slideDown(400);
            }
        },
        insertion_show_trivial_efficacy(event) {
            if (!$(`.insertion-type-trivial-efficacy`).is(":visible")) {
                $('.insertion-type-trivial-efficacy').slideDown(400);
            }
        },
        insertion_hide_trivial_efficacy(event) {
            if ($(`.insertion-type-trivial-efficacy`).is(":visible")) {
                $('.insertion-type-trivial-efficacy').hide(400);
            }
            if (!$(`.insertion-grammar-div`).is(":visible")) {
                $('.insertion-grammar-div').slideDown(400);
            }
        },
        impact_click(category, event) {
            let value = event.target.value;
            // if $(`.substitution-${value}`) is not visible, show it
            if (!$(`.${category}-impact-${value}`).is(":visible")) {
                $(`.${category}-impact-div`).hide(400);
                $(`.${category}-impact-${value}`).slideDown(400);
            }
        },
        bookmark_this_hit() {
            if ("bookmark" in this.hits_data[this.current_hit - 1]) {
                this.hits_data[this.current_hit - 1].bookmark = !this.hits_data[this.current_hit - 1].bookmark
            } else {
                this.hits_data[this.current_hit - 1].bookmark = true
            }
            // if "bookmark-active" is in classlist of ".bookmark"
            if ($(".bookmark").hasClass("bookmark-active")) {
                // remove "bookmark-active" from classlist of ".bookmark"
                $(".bookmark").removeClass("bookmark-active");
                $(`#circle-${this.current_hit}`).removeClass('circle-bookmark');
            } else {
                $(".bookmark").addClass("bookmark-active")
                $(`#circle-${this.current_hit}`).addClass('circle-bookmark');
            }
        },
        refresh_edit() {
            this.open = false;
            this.selected_span_in_original = '',
            this.selected_span_in_simplified = '',
            this.selected_span_in_original_indexs = [],
            this.selected_span_in_simplified_indexs = [],
            this.selected_edits =  {'deletion': {}, 'insertion': {}, 'substitution': {}, 'reorder':{}},
            this.selected_edits_html = "",
            this.enable_select_original_sentence = false;
            this.enable_select_simplified_sentence = false;
            $("input[name=edit_cotegory]").prop("checked", false);
            $(".checkbox-tools").prop("checked", false);
            $(".checkbox-tools-yes-no").prop("checked", false);
            $(".annotation-icon").removeClass('txt-substitution');
            $(".annotation-icon").removeClass('txt-insertion')
            $(".annotation-icon").removeClass('txt-deletion')
            $(".annotation-icon").removeClass('txt-split')
            $('.quality-selection').hide(400);
            $(".span-selection-div").hide(400);

            // insertion_annotation hide divs
            $(".insertion-type-div").hide();
            $(".insertion-type-trivial-efficacy").hide();
            $(".insertion-grammar-div").hide();

            // substitution_annotation hide divs
            $(".substitution-type-div").hide();
            $(".substitution-impact-div").hide();
            $(".substitution-coref-div").hide();
            $(".substitution-more-div").hide();
            $(".substitution-more-trivial-efficacy").hide();
            $(".substitution-grammar-div").hide();

            // reorder_annotation hide divs
            $(".reorder-impact-div").hide();

            // split_annotation hide divs
            $(".split-impact-div").hide();

            // structure_annotation hide divs
            $(".structure-impact-div").hide();
        },
        show_span_selection(event) {
            // this.process_original_html();
            // this.process_simplified_html();
            $(`.span-selection-div`).hide(400);
            $(`.span-selection-div[data-category=${event.target.value}]`).slideDown(400);
            if (event.target.value == 'deletion') {
                this.enable_select_original_sentence = true;
                this.enable_select_simplified_sentence = false;
            }  else if (event.target.value == 'substitution' || event.target.value == 'reorder') {
                this.enable_select_original_sentence = true;
                this.enable_select_simplified_sentence = true;
            } else if (event.target.value == 'split' || event.target.value == 'structure') {
                this.enable_select_original_sentence = false;
                this.enable_select_simplified_sentence = false;
            } else {
                this.enable_select_simplified_sentence = true;
                this.enable_select_original_sentence = false;
            }
        },
        async parseJsonFile(file) {
            return new Promise((resolve, reject) => {
                const fileReader = new FileReader()
                fileReader.onload = event => resolve(JSON.parse(event.target.result))
                fileReader.onerror = error => reject(error)
                fileReader.readAsText(file)
            })
        },
        async handle_file_upload(event) {
            let file = event.target.files[0];
            let new_json = await this.parseJsonFile(file)
            this.hits_data = new_json;
            this.current_hit = 1;
            for (let i = 0; i < this.hits_data.length; i++) {
                if (this.hits_data[i].annotations == undefined) {
                    this.hits_data[i].annotations = {
                        'deletion': [],
                        'substitution': [],
                        'insertion': [],
                        'split': [],
                        'reorder': [],
                        'structure': [],
                    }
                }
            }
            this.total_hits = new_json.length;
            this.process_everything();
        },
        handle_file_download() {
            var json = JSON.stringify(this.hits_data);
            var blob = new Blob([json], {type: "application/json"});
            var url = URL.createObjectURL(blob);
            var a = document.createElement("a");
            a.href = url;
            a.download = "annotations.json";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    },
    created: function () {
        let urlParams = new URLSearchParams(window.location.search);
        let original_sentece = urlParams.get('original');
        let simplified_sentence = urlParams.get('simplified');
        this.hits_data = [{
            "id": 0,
            "original": original_sentece,
            "original_spans": [],
            "simplified": simplified_sentence,
            "simplified_spans": [],
            "system": "example",
            "annotations": {
                "deletion": [],
                "substitution": [],
                "insertion": [],
                "split": [],
                "reorder": [],
                "structure": [],
            }
        }]
        this.total_hits = 1;
        this.process_everything();
    },
    mounted: function () {
    },
    computed: {
        compiled_original_html() {
            return {
                template: `<div @mousedown='deselect_original_html' @mouseup='select_original_html' id="original-sentence" class="f4 lh-paras">${this.original_html}</div>`,
                methods: {
                    click_span(event) {
                        let edits_dict = this.$parent.edits_dict
                        let category = event.target.dataset.category
                        let id = event.target.dataset.id
                        let real_id = id.split("-")[1]
                        if ($(".quality-selection").is(":visible")) {
                            if ($("input[name=edit_cotegory]:checked").val() == 'split' || $("input[name=edit_cotegory]:checked").val() == 'structure') {
                                if (real_id in this.$parent.selected_edits[category]) {
                                    delete this.$parent.selected_edits[category][real_id]
                                } else {
                                    this.$parent.selected_edits[category][real_id] = edits_dict[category][real_id]
                                }
                            }
                            this.$parent.selected_edits_html = ""
                            for (let key in this.$parent.selected_edits) {
                                for (let temp_id in this.$parent.selected_edits[key]) {
                                    let edit = this.$parent.selected_edits[key][temp_id]
                                    if (key == 'deletion') {
                                        this.$parent.selected_edits_html += `<span class="edit-type txt-${key}">delete </span>`;
                                        this.$parent.selected_edits_html += `<span class="pa1 edit-text br-pill-ns txt-${key} border-${key}-all">`;
                                        this.$parent.selected_edits_html += `&nbsp${this.$parent.hits_data[this.$parent.current_hit - 1].original.substring(edit[1],edit[2])}&nbsp`;
                                        this.$parent.selected_edits_html += `</span>`;
                                        this.$parent.selected_edits_html += ",&nbsp&nbsp";
                                    } else if (key == 'insertion') {
                                        this.$parent.selected_edits_html += `<span class="edit-type txt-${key}">insert </span>`;
                                        this.$parent.selected_edits_html += `<span class="pa1 edit-text br-pill-ns txt-${key} border-${key}-all">`;
                                        this.$parent.selected_edits_html += `&nbsp${this.$parent.hits_data[this.$parent.current_hit - 1].simplified.substring(edit[1],edit[2])}&nbsp`;
                                        this.$parent.selected_edits_html += `</span>`;
                                        this.$parent.selected_edits_html += ",&nbsp&nbsp";
                                    } else if (key == 'substitution') {
                                        this.$parent.selected_edits_html += `<span class="edit-type txt-${key}">substitute </span>`;
                                        this.$parent.selected_edits_html += `<span class="pa1 edit-text br-pill-ns txt-${key} border-${key}-all">`;
                                        this.$parent.selected_edits_html += `&nbsp${this.$parent.hits_data[this.$parent.current_hit - 1].original.substring(edit[0][1],edit[0][2])}&nbsp`;
                                        this.$parent.selected_edits_html += `</span>`;
                                        this.$parent.selected_edits_html += `<span class="edit-type txt-${key}"> with </span>`;
                                        this.$parent.selected_edits_html += `<span class="pa1 edit-text br-pill-ns txt-${key} border-${key}-all">`;
                                        this.$parent.selected_edits_html += `&nbsp${this.$parent.hits_data[this.$parent.current_hit - 1].simplified.substring(edit[1][1],edit[1][2])}&nbsp`;
                                        this.$parent.selected_edits_html += `</span>`;
                                        this.$parent.selected_edits_html += ",&nbsp&nbsp";
                                    } else if (key == 'reorder') {
                                        this.$parent.selected_edits_html += `<span class="edit-type txt-${key}">reorder </span>`;
                                        this.$parent.selected_edits_html += `<span class="pa1 edit-text br-pill-ns txt-${key} border-${key}-all">`;
                                        this.$parent.selected_edits_html += `&nbsp${this.$parent.hits_data[this.$parent.current_hit - 1].original.substring(edit[0][1],edit[0][2])}&nbsp`;
                                        this.$parent.selected_edits_html += `</span>`;
                                        this.$parent.selected_edits_html += ",&nbsp&nbsp";
                                    }
                                }
                            }
                        } else {
                            $(`.annotation-icon[data-id=${id}]`).click()
                        }
                    },
                    hover_span(event) {
                        if ($(".quality-selection").is(":visible")) {
                            return
                        }
                        let category = event.target.dataset.category
                        let spans = $(`.${category}[data-id=${event.target.dataset.id}]`)
                        spans.addClass("white")
                        let below_spans= $(`.${category}_below[data-id=${event.target.dataset.id}]`)
                        below_spans.addClass("white")
                        below_spans.removeClass(`txt-${category}`)
                        below_spans.removeClass(`txt-${category}-light`)

                        let id = event.target.dataset.id
                        let real_id = id.split("-")[1]

                        // check if bd-{category}-light is already in the class list
                        if (event.target.classList.contains(`border-${category}-light`)) {
                            spans.addClass(`bg-${category}-light`)
                            below_spans.addClass(`bg-${category}-light`)
                            try {
                                if (category == 'substitution') {
                                this.$parent.lines[category][real_id].color = "rgba(173, 197, 250, 1.0)"
                            }
                            } catch (e) {
                                console.log(e)
                            }
                        } else {
                            spans.addClass(`bg-${category}`)
                            below_spans.addClass(`bg-${category}`)
                            try {
                                if (category == 'substitution') {
                                    this.$parent.lines[category][real_id].color = "rgba(33, 134, 235, 1.0)"
                                }
                            } catch (e) {
                                console.log(e)
                            }
                        }
                    },
                    un_hover_span(event) {
                        if ($(".quality-selection").is(":visible")) {
                            return
                        }
                        let category = event.target.dataset.category
                        let spans = $(`.${category}[data-id=${event.target.dataset.id}]`)
                        spans.removeClass("white")
                        let below_spans= $(`.${category}_below[data-id=${event.target.dataset.id}]`)
                        below_spans.removeClass("white")

                        let id = event.target.dataset.id
                        let real_id = id.split("-")[1]

                        if (event.target.classList.contains(`border-${category}-light`)) {
                            below_spans.addClass(`txt-${category}-light`)
                            try {
                                if (category == 'substitution') {
                                    this.$parent.lines[category][real_id].color = "rgba(173, 197, 250, 0.4)"
                                }
                            } catch (e) {
                                console.log(e)
                            }
                        } else {
                            below_spans.addClass(`txt-${category}`)
                            try {
                                if (category == 'substitution') {
                                    this.$parent.lines[category][real_id].color = "rgba(33, 134, 235, 0.46)"
                                }
                            } catch (e) {
                                console.log(e)
                            }
                        }
                        spans.removeClass(`bg-${category}`)
                        spans.removeClass(`bg-${category}-light`)
                        below_spans.removeClass(`bg-${category}`)
                        below_spans.removeClass(`bg-${category}-light`)
                    },
                    select_original_html(event) {
                        if (!this.$parent.enable_select_original_sentence) {
                            return
                        }
                        this.$parent.process_original_html();
                        let selection = window.getSelection();
                        if (selection.anchorNode != selection.focusNode || selection.anchorNode == null) {
                            return;
                        }
                        let range = selection.getRangeAt(0);
                        let [start, end] = [range.startOffset, range.endOffset];
                        
                        if (start == end) {
                            return;
                        }
                        // manipulate start and end to try to respect word boundaries and remove
                        // whitespace.
                        end -= 1; // move to inclusive model for these computations.
                        let txt = this.$parent.hits_data[this.$parent.current_hit - 1].original
                        while (txt.charAt(start) == ' ') {
                            start += 1; // remove whitespace
                        }
                        while (start - 1 >= 0 && txt.charAt(start - 1) != ' ') {
                            start -= 1; // find word boundary
                        }
                        while (txt.charAt(end) == ' ') {
                            end -= 1; // remove whitespace
                        }
                        while (end + 1 <= txt.length - 1 && txt.charAt(end + 1) != ' ') {
                            end += 1; // find word boundary
                        }
                        // move end back to exclusive model
                        end += 1;
                        // stop if empty or invalid range after movement
                        if (start >= end) {
                            return;
                        }
                        this.$parent.selected_span_in_original = '\xa0' + txt.substring(start, end) + '\xa0'
                        let selected_category = $("input[name=edit_cotegory]:checked").val();
                        this.$parent.process_original_html_with_selected_span(selected_category, start, end);
                    },
                    deselect_original_html(event) {
                        if (!this.$parent.enable_select_original_sentence) {
                            return
                        }
                        document.getElementById("original-sentence").innerHTML = this.$parent.hits_data[this.$parent.current_hit - 1].original
                        this.$parent.original_html = this.$parent.hits_data[this.$parent.current_hit - 1].original
                    }
                },
            }
        },
        compiled_simplified_html() {
            return {
                template: `<div @mousedown='deselect_simplified_html' @mouseup='select_simplified_html' id="simplified-sentence" class="f4 lh-paras">${this.simplified_html}</div>`,
                methods: {
                    click_span(event) {
                        let edits_dict = this.$parent.edits_dict
                        let category = event.target.dataset.category
                        let id = event.target.dataset.id
                        let real_id = id.split("-")[1]
                        if ($(".quality-selection").is(":visible")) {
                            if ($("input[name=edit_cotegory]:checked").val() == 'split') {
                                let normal_id = parseInt(real_id) + 1
                                if (event.target.classList.contains(`split-sign`)) {
                                    if (normal_id == 1) {
                                        this.$parent.selected_split = `the 1st split`
                                    } else if (normal_id == 2) {
                                        this.$parent.selected_split = `the 2nd split`
                                    } else if (normal_id == 3) {
                                        this.$parent.selected_split = `the 3rd split`
                                    } else {
                                        this.$parent.selected_split = `the ${normal_id}th split`
                                    }
                                    this.$parent.selected_split_id = parseInt(real_id)
                                } else {
                                    if (real_id in this.$parent.selected_edits[category]) {
                                        delete this.$parent.selected_edits[category][real_id]
                                    } else {
                                        this.$parent.selected_edits[category][real_id] = edits_dict[category][real_id]
                                    }
                                }
                            }
                            if ($("input[name=edit_cotegory]:checked").val() == 'structure') {
                                if (real_id in this.$parent.selected_edits[category]) {
                                    delete this.$parent.selected_edits[category][real_id]
                                } else {
                                    this.$parent.selected_edits[category][real_id] = edits_dict[category][real_id]
                                }
                            }
                            this.$parent.selected_edits_html = ""
                            for (let key in this.$parent.selected_edits) {
                                for (let temp_id in this.$parent.selected_edits[key]) {
                                    let edit = this.$parent.selected_edits[key][temp_id]
                                    if (key == 'deletion') {
                                        this.$parent.selected_edits_html += `<span class="edit-type txt-${key}">delete </span>`;
                                        this.$parent.selected_edits_html += `<span class="pa1 edit-text br-pill-ns txt-${key} border-${key}-all">`;
                                        this.$parent.selected_edits_html += `&nbsp${this.$parent.hits_data[this.$parent.current_hit - 1].original.substring(edit[1],edit[2])}&nbsp`;
                                        this.$parent.selected_edits_html += `</span>`;
                                        this.$parent.selected_edits_html += ",&nbsp&nbsp";
                                    } else if (key == 'insertion') {
                                        this.$parent.selected_edits_html += `<span class="edit-type txt-${key}">insert </span>`;
                                        this.$parent.selected_edits_html += `<span class="pa1 edit-text br-pill-ns txt-${key} border-${key}-all">`;
                                        this.$parent.selected_edits_html += `&nbsp${this.$parent.hits_data[this.$parent.current_hit - 1].simplified.substring(edit[1],edit[2])}&nbsp`;
                                        this.$parent.selected_edits_html += `</span>`;
                                        this.$parent.selected_edits_html += ",&nbsp&nbsp";
                                    } else if (key == 'substitution') {
                                        this.$parent.selected_edits_html += `<span class="edit-type txt-${key}">substitute </span>`;
                                        this.$parent.selected_edits_html += `<span class="pa1 edit-text br-pill-ns txt-${key} border-${key}-all">`;
                                        this.$parent.selected_edits_html += `&nbsp${this.$parent.hits_data[this.$parent.current_hit - 1].original.substring(edit[0][1],edit[0][2])}&nbsp`;
                                        this.$parent.selected_edits_html += `</span>`;
                                        this.$parent.selected_edits_html += `<span class="edit-type txt-${key}"> with </span>`;
                                        this.$parent.selected_edits_html += `<span class="pa1 edit-text br-pill-ns txt-${key} border-${key}-all">`;
                                        this.$parent.selected_edits_html += `&nbsp${this.$parent.hits_data[this.$parent.current_hit - 1].simplified.substring(edit[1][1],edit[1][2])}&nbsp`;
                                        this.$parent.selected_edits_html += `</span>`;
                                        this.$parent.selected_edits_html += ",&nbsp&nbsp";
                                    } else if (key == 'reorder') {
                                        this.$parent.selected_edits_html += `<span class="edit-type txt-${key}">reorder </span>`;
                                        this.$parent.selected_edits_html += `<span class="pa1 edit-text br-pill-ns txt-${key} border-${key}-all">`;
                                        this.$parent.selected_edits_html += `&nbsp${this.$parent.hits_data[this.$parent.current_hit - 1].original.substring(edit[0][1],edit[0][2])}&nbsp`;
                                        this.$parent.selected_edits_html += `</span>`;
                                        this.$parent.selected_edits_html += ",&nbsp&nbsp";
                                    }
                                }
                            }
                        } else {
                            $(`.annotation-icon[data-id=${id}]`).click()
                        }
                    },
                    hover_span(event) {
                        if ($(".quality-selection").is(":visible")) {
                            return
                        }
                        let category = event.target.dataset.category
                        let spans = $(`.${category}[data-id=${event.target.dataset.id}]`)
                        spans.addClass("white")

                        let split_signs = $(`.split-sign[data-id=${event.target.dataset.id}]`)

                        let below_spans= $(`.${category}_below[data-id=${event.target.dataset.id}]`)
                        below_spans.addClass("white")
                        below_spans.removeClass(`txt-${category}`)
                        below_spans.removeClass(`txt-${category}-light`)

                        let id = event.target.dataset.id
                        let real_id = id.split("-")[1]
                        if (event.target.classList.contains(`split-sign`)) {
                            if (event.target.classList.contains(`txt-${category}-light`)) {
                                spans.addClass(`bg-${category}-light`)
                                spans.addClass(`white`)
                                spans.removeClass(`txt-${category}-light`)
                                below_spans.addClass(`bg-${category}-light`)
                                return
                            } else {
                                spans.addClass(`bg-${category}`)
                                spans.addClass(`white`)
                                spans.removeClass(`txt-${category}`)
                                below_spans.addClass(`bg-${category}`)
                                return
                            }
                        }

                        // check if bd-{category}-light is already in the class list
                        if (event.target.classList.contains(`border-${category}-light`)) {
                            spans.addClass(`bg-${category}-light`)
                            if (category == 'split') {
                                split_signs.removeClass(`txt-${category}-light`)
                            }
                            below_spans.addClass(`bg-${category}-light`)
                            try {
                                if (category == 'substitution') {
                                    this.$parent.lines[category][real_id].color = "rgba(173, 197, 250, 1.0)"
                                }
                            } catch (e) {
                                console.log(e)
                            }
                            
                        } else {
                            spans.addClass(`bg-${category}`)
                            if (category == 'split') {
                                split_signs.removeClass(`txt-${category}`)
                            }
                            below_spans.addClass(`bg-${category}`)
                            try {
                                if (category == 'substitution') {
                                    this.$parent.lines[category][real_id].color = "rgba(33, 134, 235, 1.0)"
                                }
                            } catch (e) {
                                console.log(e)
                            }
                        }
                    },
                    un_hover_span(event) {
                        if ($(".quality-selection").is(":visible")) {
                            return
                        }
                        let category = event.target.dataset.category
                        let spans = $(`.${category}[data-id=${event.target.dataset.id}]`)
                        spans.removeClass("white")

                        let split_signs = $(`.split-sign[data-id=${event.target.dataset.id}]`)

                        let below_spans= $(`.${category}_below[data-id=${event.target.dataset.id}]`)
                        below_spans.removeClass("white")

                        let id = event.target.dataset.id
                        let real_id = id.split("-")[1]

                        let below_spans_class_list = below_spans.attr('class').split(/\s+/)
                        if (event.target.classList.contains(`split-sign`)) {
                            if (below_spans_class_list.includes(`bg-${category}-light`)) {
                                spans.removeClass(`bg-${category}-light`)
                                spans.removeClass(`white`)
                                split_signs.addClass(`txt-${category}-light`)
                                below_spans.removeClass(`bg-${category}-light`)
                                below_spans.addClass(`txt-${category}-light`)
                                return
                            } else {
                                spans.removeClass(`bg-${category}`)
                                spans.removeClass(`white`)
                                split_signs.addClass(`txt-${category}`)
                                below_spans.removeClass(`bg-${category}`)
                                below_spans.addClass(`txt-${category}`)
                                return
                            }
                        }

                        if (event.target.classList.contains(`border-${category}-light`)) {
                            below_spans.addClass(`txt-${category}-light`)
                            if (category == 'split') {
                                split_signs.addClass(`txt-${category}-light`)
                            }
                            try {
                                if (category == 'substitution') {
                                    this.$parent.lines[category][real_id].color = "rgba(173, 197, 250, 0.4)"
                                }
                            } catch (e) {
                                console.log(e)
                            }
                        } else {
                            below_spans.addClass(`txt-${category}`)
                            if (category == 'split') {
                                split_signs.addClass(`txt-${category}`)
                            }
                            try {
                                if (category == 'substitution') {
                                    console.log(this.$parent.lines[category])
                                    this.$parent.lines[category][real_id].color = "rgba(33, 134, 235, 0.46)"
                                }
                            } catch (e) {
                                console.log(e)
                            }
                        }
                        spans.removeClass(`bg-${category}`)
                        spans.removeClass(`bg-${category}-light`)
                        below_spans.removeClass(`bg-${category}`)
                        below_spans.removeClass(`bg-${category}-light`)
                    },
                    select_simplified_html(event) {
                        if (!this.$parent.enable_select_simplified_sentence) {
                            return
                        }
                        let selection = window.getSelection();
                        if (selection.anchorNode != selection.focusNode || selection.anchorNode == null) {
                            this.$parent.process_simplified_html()
                            return;
                        }
                        let range = selection.getRangeAt(0);
                        let [start, end] = [range.startOffset, range.endOffset];
                        
                        // if (start == end) {
                        //     this.$parent.process_simplified_html()
                        //     return;
                        // }
                        // manipulate start and end to try to respect word boundaries and remove
                        // whitespace.
                        end -= 1; // move to inclusive model for these computations.
                        let txt = this.$parent.hits_data[this.$parent.current_hit - 1].simplified
                        while (txt.charAt(start) == ' ') {
                            start += 1; // remove whitespace
                        }
                        while (start - 1 >= 0 && txt.charAt(start - 1) != ' ') {
                            start -= 1; // find word boundary
                        }
                        while (txt.charAt(end) == ' ') {
                            end -= 1; // remove whitespace
                        }
                        while (end + 1 <= txt.length - 1 && txt.charAt(end + 1) != ' ') {
                            end += 1; // find word boundary
                        }
                        // move end back to exclusive model
                        end += 1;
                        // stop if empty or invalid range after movement
                        if (start >= end) {
                            this.$parent.process_simplified_html()
                            return;
                        }
                        this.$parent.selected_span_in_simplified = '\xa0' + txt.substring(start, end) + '\xa0'
                        let selected_category = $("input[name=edit_cotegory]:checked").val();
                        this.$parent.process_simplified_html_with_selected_span(selected_category, start, end);
                    },
                    deselect_simplified_html(event) {
                        if (!this.$parent.enable_select_simplified_sentence) {
                            return
                        }
                        document.getElementById("simplified-sentence").innerHTML = this.$parent.hits_data[this.$parent.current_hit - 1].simplified
                        this.$parent.simplified_html = this.$parent.hits_data[this.$parent.current_hit - 1].simplified
                    }
                }
            }
        },
        compiled_edits_html() {
            return {
                template: `<div class="f4 lh-paras">${this.edits_html}</div>`,
                methods: {
                    hover_span(event) {
                        if ($(".quality-selection").is(":visible")) {
                            return
                        }
                        // console.log(this.$parent.hits_data)
                        // if the target is a span, go to the parent div
                        let target = event.target
                        if (target.tagName == 'SPAN' && target.parentElement.tagName != 'DIV') {
                            if (target.parentElement.parentElement.tagName != 'DIV') {
                                target = target.parentElement.parentElement
                            } else {
                                target = target.parentElement
                            }
                        } else if (target.tagName == 'I') {
                            target = target.parentElement.parentElement
                        }
                        let category = target.dataset.category
                        let spans = $(`.${category}[data-id=${target.dataset.id}]`)
                        spans.addClass("white")

                        let split_signs = $(`.split-sign[data-id=${target.dataset.id}]`)

                        let below_spans= $(`.${category}_below[data-id=${target.dataset.id}]`)
                        below_spans.addClass("white")
                        below_spans.removeClass(`txt-${category}`)
                        below_spans.removeClass(`txt-${category}-light`)

                        
                        let classList = below_spans.attr("class").split(/\s+/);

                        let real_id = target.dataset.id.split("-")[1]

                        // check if bd-{category}-light is already in the class list
                        if (classList.includes(`border-${category}-light-all`)) {
                            split_signs.removeClass(`txt-${category}-light`)
                            spans.addClass(`bg-${category}-light`)
                            below_spans.addClass(`bg-${category}-light`)
                            if (category == 'substitution') {
                                this.$parent.lines[category][real_id].color = "rgba(173, 197, 250, 1.0)"
                            }
                        } else {
                            split_signs.removeClass(`txt-${category}`)
                            spans.addClass(`bg-${category}`)
                            below_spans.addClass(`bg-${category}`)
                            if (category == 'substitution') {
                                this.$parent.lines[category][real_id].color = "rgba(33, 134, 235, 1.0)"
                            }
                        }
                    },
                    un_hover_span(event) {
                        if ($(".quality-selection").is(":visible")) {
                            return
                        }
                        // if the target is a span, go to the parent div
                        let target = event.target
                        if (target.tagName == 'SPAN' && target.parentElement.tagName != 'DIV') {
                            if (target.parentElement.parentElement.tagName != 'DIV') {
                                target = target.parentElement.parentElement
                            } else {
                                target = target.parentElement
                            }
                        } else if (target.tagName == 'I') {
                            target = target.parentElement.parentElement
                        }
                        let category = target.dataset.category
                        let spans = $(`.${category}[data-id=${target.dataset.id}]`)
                        spans.removeClass("white")

                        let split_signs = $(`.split-sign[data-id=${target.dataset.id}]`)

                        let below_spans= $(`.${category}_below[data-id=${target.dataset.id}]`)
                        below_spans.removeClass("white")

                        let classList = below_spans.attr("class").split(/\s+/);

                        let real_id = target.dataset.id.split("-")[1]

                        if (classList.includes(`border-${category}-light-all`)) {
                            split_signs.addClass(`txt-${category}-light`)
                            below_spans.addClass(`txt-${category}-light`)
                            if (category == 'substitution') {
                                this.$parent.lines[category][real_id].color = "rgba(173, 197, 250, 0.4)"
                            }
                        } else {
                            split_signs.addClass(`txt-${category}`)
                            below_spans.addClass(`txt-${category}`)
                            if (category == 'substitution') {
                                this.$parent.lines[category][real_id].color = "rgba(33, 134, 235, 0.46)"
                            }
                        }
                        spans.removeClass(`bg-${category}`)
                        spans.removeClass(`bg-${category}-light`)
                        below_spans.removeClass(`bg-${category}`)
                        below_spans.removeClass(`bg-${category}-light`)
                    },
                    annotate_edit(event) {
                        let target = event.target
                        let category = target.dataset.category

                        if(this.$parent.open){
                            $(`.quality-selection[data-category=${category}]`).hide(400);
                            this.$parent.refresh_edit();
                            return;
                        } else{
                            $(`.quality-selection`).hide(400)
                            $(`.quality-selection[data-category=${category}]`).slideDown(400);
                            $(event.target).addClass(`txt-${category}`)
                            this.$parent.open = !this.$parent.open;
                        }

                        let id = target.dataset.id
                        
                        let edit_dict = this.$parent.edits_dict
                        let real_id = id.split("-")[1]

                        if (category == "insertion") {
                            this.$parent.current_insertion_edit_id = real_id
                        }

                        let spans = $(`.${category}[data-id=${id}]`)
                        spans.addClass("white")
                        spans.removeClass(`border-${category}-light`)
                        spans.addClass(`border-${category}`)
                        spans.addClass(`bg-${category}`)

                        // below_spans.addClass(`bg-${category}`)
                        
                        let original_sentence = this.$parent.hits_data[this.$parent.current_hit - 1].original
                        let simplified_sentence = this.$parent.hits_data[this.$parent.current_hit - 1].simplified
                        // parse the real_id to int
                        real_id = parseInt(real_id)

                        if (category == "substitution" || category == "reorder") {
                            let annotating_span_orginal = edit_dict[category][real_id][0]
                            let annotating_span_simplified = edit_dict[category][real_id][1]
                            this.$parent.annotating_edit_span_in_original = original_sentence.substring(annotating_span_orginal[1], annotating_span_orginal[2])
                            this.$parent.annotating_edit_span_in_simplified = simplified_sentence.substring(annotating_span_simplified[1], annotating_span_simplified[2])
                        } else if (category == "split") {
                            this.$parent.annotating_edit_span_for_split = ""
                            let category_id_dict = edit_dict[category][real_id]
                            let key = category
                            let light = ""
                            let first_span = 0
                            for (let current_category in category_id_dict) {
                                if (current_category == "split") {
                                    continue
                                }
                                let current_category_short = this.$parent.key_to_key_short[current_category]
                                for (let j in category_id_dict[current_category]) {
                                    if (first_span == 0) {
                                        this.$parent.annotating_edit_span_for_split += `<span class="edit-type txt-${key}${light} f3"> (</span>`;
                                        first_span = 1;
                                    } else {
                                        this.$parent.annotating_edit_span_for_split += `<span class="edit-type txt-${key}${light} f3"> , </span>`;
                                    }
                                    if (current_category == "insertion") {
                                        this.$parent.annotating_edit_span_for_split += `<span class="edit-type txt-${key}${light} f3"> ${current_category_short} </span>`;
                                        this.$parent.annotating_edit_span_for_split += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${real_id}" data-category="${key}">`;
                                        this.$parent.annotating_edit_span_for_split += `&nbsp${simplified_sentence.substring(category_id_dict[current_category][j][1], category_id_dict[current_category][j][2])}&nbsp`;
                                        this.$parent.annotating_edit_span_for_split += `</span>`;
                                    } else if (current_category == "deletion") {
                                        this.$parent.annotating_edit_span_for_split += `<span class="edit-type txt-${key}${light} f3"> ${current_category_short} </span>`;
                                        this.$parent.annotating_edit_span_for_split += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${real_id}" data-category="${key}">`;
                                        this.$parent.annotating_edit_span_for_split += `&nbsp${original_sentence.substring(category_id_dict[current_category][j][1], category_id_dict[current_category][j][2])}&nbsp`;
                                        this.$parent.annotating_edit_span_for_split += `</span>`;
                                    } else if (current_category == "substitution") {
                                        this.$parent.annotating_edit_span_for_split += `<span class="edit-type txt-${key}${light} f3"> ${current_category_short} </span>`;
                                        this.$parent.annotating_edit_span_for_split += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${real_id}" data-category="${key}">`;
                                        this.$parent.annotating_edit_span_for_split += `&nbsp${original_sentence.substring(category_id_dict[current_category][j][0][1], category_id_dict[current_category][j][0][2])}&nbsp`;
                                        this.$parent.annotating_edit_span_for_split += `</span>`;
                                        this.$parent.annotating_edit_span_for_split += `<span class="edit-type txt-${key}${light} f3"> with </span>`;
                                        this.$parent.annotating_edit_span_for_split += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${real_id}" data-category="${key}">`;
                                        this.$parent.annotating_edit_span_for_split += `&nbsp${simplified_sentence.substring(category_id_dict[current_category][j][1][1], category_id_dict[current_category][j][1][2])}&nbsp`;
                                        this.$parent.annotating_edit_span_for_split += `</span>`;
                                    } else if (current_category == "reorder") {
                                        this.$parent.annotating_edit_span_for_split += `<span class="edit-type txt-${key}${light} f3"> ${current_category_short} </span>`;
                                        this.$parent.annotating_edit_span_for_split += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${real_id}" data-category="${key}">`;
                                        this.$parent.annotating_edit_span_for_split += `&nbsp${original_sentence.substring(category_id_dict[current_category][j][0][1], category_id_dict[current_category][j][0][2])}&nbsp`;
                                        this.$parent.annotating_edit_span_for_split += `</span>`;
                                    }
                                }
                            }
                            if (first_span == 1) {
                                this.$parent.annotating_edit_span_for_split += `<span class="edit-type txt-${key}${light} f3"> ) </span>`;
                            }
                        } else if (category == "structure") {
                            this.$parent.annotating_edit_span_for_structure = ""
                            let category_id_dict = edit_dict[category][real_id]
                            let key = category
                            let light = ""
                            let first_span = 0
                            for (let current_category in category_id_dict) {
                                let current_category_short = this.$parent.key_to_key_short[current_category]
                                for (let j in category_id_dict[current_category]) {
                                    if (first_span == 0) {
                                        this.$parent.annotating_edit_span_for_structure += `<span class="edit-type txt-${key}${light} f3"> (</span>`;
                                        first_span = 1;
                                    } else {
                                        this.$parent.annotating_edit_span_for_structure += `<span class="edit-type txt-${key}${light} f3"> , </span>`;
                                    }
                                    if (current_category == "insertion") {
                                        this.$parent.annotating_edit_span_for_structure += `<span class="edit-type txt-${key}${light} f3"> ${current_category_short} </span>`;
                                        this.$parent.annotating_edit_span_for_structure += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${real_id}" data-category="${key}">`;
                                        this.$parent.annotating_edit_span_for_structure += `&nbsp${simplified_sentence.substring(category_id_dict[current_category][j][1], category_id_dict[current_category][j][2])}&nbsp`;
                                        this.$parent.annotating_edit_span_for_structure += `</span>`;
                                    } else if (current_category == "deletion") {
                                        this.$parent.annotating_edit_span_for_structure += `<span class="edit-type txt-${key}${light} f3"> ${current_category_short} </span>`;
                                        this.$parent.annotating_edit_span_for_structure += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${real_id}" data-category="${key}">`;
                                        this.$parent.annotating_edit_span_for_structure += `&nbsp${original_sentence.substring(category_id_dict[current_category][j][1], category_id_dict[current_category][j][2])}&nbsp`;
                                        this.$parent.annotating_edit_span_for_structure += `</span>`;
                                    } else if (current_category == "substitution") {
                                        this.$parent.annotating_edit_span_for_structure += `<span class="edit-type txt-${key}${light} f3"> ${current_category_short} </span>`;
                                        this.$parent.annotating_edit_span_for_structure += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${real_id}" data-category="${key}">`;
                                        this.$parent.annotating_edit_span_for_structure += `&nbsp${original_sentence.substring(category_id_dict[current_category][j][0][1], category_id_dict[current_category][j][0][2])}&nbsp`;
                                        this.$parent.annotating_edit_span_for_structure += `</span>`;
                                        this.$parent.annotating_edit_span_for_structure += `<span class="edit-type txt-${key}${light} f3"> with </span>`;
                                        this.$parent.annotating_edit_span_for_structure += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${real_id}" data-category="${key}">`;
                                        this.$parent.annotating_edit_span_for_structure += `&nbsp${simplified_sentence.substring(category_id_dict[current_category][j][1][1], category_id_dict[current_category][j][1][2])}&nbsp`;
                                        this.$parent.annotating_edit_span_for_structure += `</span>`;
                                    } else if (current_category == "reorder") {
                                        this.$parent.annotating_edit_span_for_structure += `<span class="edit-type txt-${key}${light} f3"> ${current_category_short} </span>`;
                                        this.$parent.annotating_edit_span_for_structure += `<span class="pa1 edit-text br-pill-ns txt-${key}${light} border-${key}${light}-all ${key}_below" data-id="${key}-${real_id}" data-category="${key}">`;
                                        this.$parent.annotating_edit_span_for_structure += `&nbsp${original_sentence.substring(category_id_dict[current_category][j][0][1], category_id_dict[current_category][j][0][2])}&nbsp`;
                                        this.$parent.annotating_edit_span_for_structure += `</span>`;
                                    }
                                }
                            }
                            if (first_span == 1) {
                                this.$parent.annotating_edit_span_for_structure += `<span class="edit-type txt-${key}${light} f3"> ) </span>`;
                            }
                        } else {
                            let annotating_span = edit_dict[category][real_id]

                            if (annotating_span[0] == 0) {
                                this.$parent.annotating_edit_span_in_original = original_sentence.substring(annotating_span[1], annotating_span[2])
                            } else {
                                this.$parent.annotating_edit_span_in_simplified = simplified_sentence.substring(annotating_span[1], annotating_span[2])
                            }
                        }
                        this.$parent.annotating_edit_span_category_id = real_id
                    },
                    trash_edit(event) {
                        let target = event.target
                        let category = target.dataset.category
                        let id = target.dataset.id
                        let original_spans = this.$parent.hits_data[this.$parent.current_hit - 1].original_spans
                        let simplified_spans = this.$parent.hits_data[this.$parent.current_hit - 1].simplified_spans
                        let category_id = this.$parent.category_to_id[category]
                        //  real_id is the numebr after "-" in id
                        let real_id = id.split("-")[1]
                        // parse the real_id to int
                        real_id = parseInt(real_id)

                        let newspans = []
                        for (let i = 0; i < original_spans.length; i++) {
                            if (original_spans[i][0] == category_id && original_spans[i][3] == real_id) {
                                continue
                            }
                            newspans.push(original_spans[i])
                        }

                        let newspans_simplified = []
                        for (let i = 0; i < simplified_spans.length; i++) {
                            if (simplified_spans[i][0] == category_id && simplified_spans[i][3] == real_id) {
                                continue
                            }
                            newspans_simplified.push(simplified_spans[i])
                        }
                        
                        this.$parent.hits_data[this.$parent.current_hit - 1].original_spans = newspans
                        this.$parent.hits_data[this.$parent.current_hit - 1].simplified_spans = newspans_simplified
                        delete this.$parent.hits_data[this.$parent.current_hit - 1]["annotations"][category][real_id]
                        this.$parent.process_everything();
                    }
                },
                mounted: function () {
                    $(`#circle-${this.$parent.current_hit}`).addClass('circle-active');
                    
                    for (let category in this.$parent.lines) {
                        for (let i in this.$parent.lines[category]) {
                            if (category == "substitution" || category == "reorder") {
                                this.$parent.lines[category][i].remove()
                            } else {
                                for (let j in this.$parent.lines[category][i]) {
                                    this.$parent.lines[category][i][j].remove()
                                }
                            }
                        }
                    }
                    this.$parent.lines = {"split":{}, "substitution":{}, "reorder":{}, "structure":{}}

                    let substitution_edits_dict = this.$parent.edits_dict["substitution"]
                    if ($('.substitution.original_span')[0] != null) {
                        for (let id in substitution_edits_dict) {
                            let color = "rgba(173, 197, 250, 0.4)"
                            if (("annotations" in this.$parent.hits_data[[this.$parent.current_hit - 1]]) && (id in this.$parent.hits_data[[this.$parent.current_hit - 1]].annotations["substitution"])) {
                                color = "rgba(33, 134, 235, 0.46)"
                            }
                            this.$parent.lines["substitution"][id] = new LeaderLine(
                                $(`.substitution.original_span[data-id='substitution-${id}']`)[0],
                                $(`.substitution.simplified_span[data-id='substitution-${id}']`)[0],
                                {endPlug: "behind",
                                size: 3,
                                path: "straight",
                                color: color,}
                            )
                        }
                    }
                    
                    let reorder_edits_dict = this.$parent.edits_dict["reorder"]
                    if ($('.reorder.original_span')[0] != null) {
                        for (let id in reorder_edits_dict) {
                            let color = "rgba(182, 227, 229, 0.4)"
                            if (("annotations" in this.$parent.hits_data[[this.$parent.current_hit - 1]]) && (id in this.$parent.hits_data[[this.$parent.current_hit - 1]].annotations["reorder"])) {
                                color = "rgba(60, 163, 167, 0.46)"
                            }
                            this.$parent.lines["reorder"][id] = new LeaderLine(
                                $(`.reorder.original_span[data-id='reorder-${id}']`)[0],
                                $(`.reorder.simplified_span[data-id='reorder-${id}']`)[0],
                                {endPlug: "behind",
                                size: 3,
                                path: "straight",
                                color: color,}
                            )
                        }
                    }


                    let split_edits_dict = this.$parent.edits_dict["split"]
                    if (split_edits_dict != {}) {
                        for (let id in split_edits_dict) {
                            let color = "rgba(250, 229, 175, 0.4)"
                            if (("annotations" in this.$parent.hits_data[[this.$parent.current_hit - 1]]) && (id in this.$parent.hits_data[[this.$parent.current_hit - 1]].annotations["split"])) {
                                color = "rgba(33, 134, 235, 0.46)"
                            }
                            this.$parent.lines["split"][id] = []
                            for (let span_category in split_edits_dict[id]) {
                                for (let span_id in split_edits_dict[id][span_category]) {
                                    let span = split_edits_dict[id][span_category][span_id]
                                    if (span_category == "deletion") {
                                        this.$parent.lines["split"][id].push(
                                            new LeaderLine(
                                            $(`.split.original_span[data-id='split-${id}'][data-childcategory=${span_category}][data-childid=${span_id}]`)[0],
                                            $(`.split.split-sign[data-id='split-${id}']`)[0],
                                            {endPlug: "arrow3",
                                            size: 3,
                                            path: "straight",
                                            color: color,})
                                        )
                                    } else if (span_category =="insertion") {
                                        this.$parent.lines["split"][id].push(
                                            new LeaderLine(
                                            $(`.split.simplified_span[data-id='split-${id}'][data-childcategory=${span_category}][data-childid=${span_id}]`)[0],
                                            $(`.split.split-sign[data-id='split-${id}']`)[0],
                                            {endPlug: "arrow3",
                                            size: 3,
                                            path: "arc",
                                            color: color,})
                                        )
                                    } else if (span_category == "substitution" || span_category == "reorder") {
                                        this.$parent.lines["split"][id].push(
                                            new LeaderLine(
                                            $(`.split.original_span[data-id='split-${id}'][data-childcategory=${span_category}][data-childid=${span_id}]`)[0],
                                            $(`.split.simplified_span[data-id='split-${id}'][data-childcategory=${span_category}][data-childid=${span_id}]`)[0],
                                            {endPlug: "behind",
                                            size: 3,
                                            path: "straight",
                                            color: color,})
                                        )

                                        this.$parent.lines["split"][id].push(
                                            new LeaderLine(
                                            $(`.split.simplified_span[data-id='split-${id}'][data-childcategory=${span_category}][data-childid=${span_id}]`)[0],
                                            $(`.split.split-sign[data-id='split-${id}']`)[0],
                                            {endPlug: "arrow3",
                                            size: 3,
                                            path: "arc",
                                            color: color,})
                                        )
                                    }
                                }
                            }
                        }
                    }

                    let structure_edits_dict = this.$parent.edits_dict["structure"]
                    if (structure_edits_dict != {}) {
                        for (let id in structure_edits_dict) {
                            let color = "rgba(242, 189, 161, 0.4)"
                            if (("annotations" in this.$parent.hits_data[[this.$parent.current_hit - 1]]) && (id in this.$parent.hits_data[[this.$parent.current_hit - 1]].annotations["structure"])) {
                                color = "rgba(230, 124, 67, 0.46)"
                            }
                            this.$parent.lines["structure"][id] = []
                            for (let span_category in structure_edits_dict[id]) {
                                for (let span_id in structure_edits_dict[id][span_category]) {
                                    let span = structure_edits_dict[id][span_category][span_id]
                                    if (span_category == "substitution" || span_category == "reorder") {
                                        this.$parent.lines["structure"][id].push(
                                            new LeaderLine(
                                            $(`.structure.original_span[data-id='structure-${id}'][data-childcategory=${span_category}][data-childid=${span_id}]`)[0],
                                            $(`.structure.simplified_span[data-id='structure-${id}'][data-childcategory=${span_category}][data-childid=${span_id}]`)[0],
                                            {endPlug: "behind",
                                            size: 3,
                                            path: "straight",
                                            color: color,})
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        compiled_split_annotating_span(){
            return {
                template: `${this.annotating_edit_span_for_split}`,
            }
        },
        compiled_structure_annotating_span(){
            return {
                template: `${this.annotating_edit_span_for_structure}`,
            }
        },
        total_edits () {
            if (this.hits_data == null) {
                return 0
            } else {
                // console.log(this.edits_dict)
                // iterate through the edits_dict and count the number of edits
                let total_num = 0
                for (let category in this.edits_dict) {
                    let category_dict = this.edits_dict[category]
                    for (let id in category_dict) {
                        total_num += 1
                    }
                }
                return total_num
            }
        },
        annotated_edits () {
            if (this.hits_data == null) {
                return 0
            } else {
                let total_num = 0
                for (let category in this.hits_data[[this.current_hit - 1]].annotations) {
                    let category_dict = this.hits_data[[this.current_hit - 1]].annotations[category]
                    for (let id in category_dict) {
                        total_num += 1
                    }
                }
                return total_num
            }
        },
        save_validated_deletion () {
            return false
        },
        save_validated_insertion () {
            return false
        },
        save_validated_split () {
            return false
        },
        save_validated_substitution () {
            return false
        },
        save_validated_reorder () {
            return false
        },
        save_validated_structure () {
            return false
        }
    },
})


app.mount('#app')
