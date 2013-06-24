define(function(require) {
	var Marionette = require('backbone.marionette');
	require('backbone.stickit');
	require('bootstrap/colorpicker');

	return Marionette.ItemView.extend({
		template: '#point-template',
		tagName: 'div',
		className: 'accordion-group',
		model: null,
		events: {
			'click .download': 'onToggleDownload',
			'click .save': 'onSave',
			'click .cancel': 'onCancel',
			'click .delete': 'onDelete',
			'colorChange .colorpicker': 'onColorChange'
		},
		ui: {
			accordion: '.accordion-body'
		},
		bindings: {
			'.point-name': 'name',
			'.swatch': {
				attributes: [
					{
						name: "style",
						observe: "color",
						onGet: function(val) {
							return "background-color: " + val + ";";
						}
					}
				]
			},
			'.accordion-toggle': {
				attributes: [
					{
						name: 'href',
						observe: 'id',
						onGet: function(val) {
							return '#' + this.makeIdAttr(val);
						}
					}
				]
			},
			'.accordion-body': {
				attributes: [
					{
						name: 'id',
						observe: 'id',
						onGet: 'makeIdAttr'
					}
				]
			},
			'[name="color"]': 'color',
			'[name="name"]': 'name',
			'[name="x_coord"]': 'x',
			'[name="z_coord"]': 'z',
			'[name="y_coord"]': 'y',
			'[name="poiType"]': 'poiType',
			'[name="dimension"]': 'dimension'
		},
		initialize: function() {
			_(this).bindAll('makeIdAttr', 'onSaveSuccess', 'onSaveFail',
				'onSaveComplete', 'togglePoint');
			this.on('close', this.unstickit);
		},
		togglePoint: function(cid) {
			if( cid === this.model.cid ) {
				this.ui.accordion.collapse('show');
			}
			else if (this.ui.accordion.hasClass('in') ) {
				this.ui.accordion.collapse('hide');
			}
		},
		makeIdAttr: function(objId) {
			return 'point_' + objId;
		},
		onRender: function() {
			this.$('.colorpicker').colorpicker({format: 'hex'});
			this.stickit();
		},
		onToggleDownload: function(e) {
			e.preventDefault();
			$(e.currentTarget).toggleClass('btn-success btn-danger');
		},
		onColorChange: function(e) {
			this.$('.swatch').backgroundColor(e.color.toHex());
		},
		onCancel: function(e) {
			e.preventDefault();
		},
		onDelete: function(e) {
			e.preventDefault();
		},
		onSave: function(e) {
			e.preventDefault();
			this.model.save();
			// .success, .done, .fail callbacks.
			// TODO: Implement this
		},
		onSaveSuccess: function() {

		},
		onSaveFail: function() {

		},
		onSaveComplete: function() {

		}
	});
});