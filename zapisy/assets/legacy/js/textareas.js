tinymce.init({
	selector:'textarea.tinymce',
	theme: 'modern',
	toolbar1: 'removeformat undo redo paste | alignleft aligncenter alignright | formatselect forecolor backcolor | table hr',
	toolbar2: 'bold italic underline strikethrough | bullist numlist outdent indent | link unlink subscript superscript nonbreaking code',
	plugins: 'advlist autolink link code hr preview fullscreen lists table paste nonbreaking textcolor',
	toolbar_items_size: 'small',
	language: 'pl',
	entity_encoding: 'raw',
	resize: "both",
	menubar: false
});
