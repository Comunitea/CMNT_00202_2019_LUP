odoo.define('custom_stock_barcode.production_client_action', function (require) {
'use strict';

var core = require('web.core');
var ClientAction = require('stock_barcode.ClientAction');
var ViewsWidget = require('stock_barcode.ViewsWidget');

var _t = core._t;

var ProductionClientAction = ClientAction.extend({
    custom_events: _.extend({}, ClientAction.prototype.custom_events, {
        'print_flabel': '_onPrintFinishedLabel',
        'print_production': '_onPrintProduction',
        'production_scrap': '_onScrap',
        'validate': '_onProduce',
        'cancel': '_onCancel',
        'create_incident': '_onCreateIncident',
        'mark_as_done': '_onMarkAsDone',
        'button_assign': '_onButtonAssign',
        'ok_quality': '_onOkQuality',
    }),

    init: function (parent, action) {
        this._super.apply(this, arguments);
        this.context = action.context;
        this.commands['O-BTN.scrap'] = this._scrap.bind(this);
        this.commands['O-BTN.produce'] = this._onProduce.bind(this);
        this.commands['O-BTN.cancel'] = this._cancel.bind(this);
        this.commands['O-BTN.print_flabel'] = this._onPrintFinishedLabel.bind(this);
        this.commands['O-BTN.print_production'] = this._onPrintProduction.bind(this);
        this.commands['O-BTN.create_incident'] = this._onCreateIncident.bind(this);
        this.commands['O-BTN.o_mark_as_done_page'] = this._onMarkAsDone.bind(this);
        this.commands['O-BTN.o_button_assign'] = this._onButtonAssign.bind(this);
        this.commands['O-BTN.o_ok_quality_page'] = this._onOkQuality.bind(this);
        if (! this.actionParams.productionId) {
            this.actionParams.productionId = action.context.active_id;
            this.actionParams.model = 'mrp.production';
        }
        this.ok_tech = undefined;
        this.availability = undefined;
        this.is_locked = undefined;
        this.routing_id = undefined;
        this.check_to_done = undefined;
        this.state = undefined;
        this.company_id = undefined;
        this.all_wo_done = undefined;
        this.quantity_not_available = undefined;
    },

    willStart: function () {
        var self = this;
        var recordId = this.actionParams.pickingId || this.actionParams.inventoryId || this.actionParams.productionId;
        return $.when(
            self._getState(recordId),
            self._getProductBarcodes(),
            self._getLocationBarcodes(),
            self._getProductDefaultCodes(),
            self._getProductProviderCodes()
        ).then(function () {
            self._loadNomenclature();
            var picking_type_code = self.currentState.picking_type_code;
            var production_state = self.currentState.state;
            this.ok_tech = self.currentState.ok_tech;
            this.availability = self.currentState.availability;
            this.is_locked = self.currentState.is_locked;
            this.state = self.currentState.state;
            this.routing_id = self.currentState.routing_id;
            this.check_to_done = self.currentState.check_to_done;
            this.company_id = self.currentState.company_id;
            this.all_wo_done = self.currentState.all_wo_done;
            this.quantity_not_available = self.currentState.quantity_not_available;
            if (picking_type_code === 'incoming') {
                self.mode = 'receipt';
            } else if (picking_type_code === 'outgoing') {
                self.mode = 'delivery';
            } else {
                self.mode = 'internal';
            }

            if (self.currentState.group_stock_multi_locations === false) {
                self.mode = 'no_multi_locations';
            }

            if (production_state === 'done') {
                self.mode = 'done';
            } else if (production_state === 'cancel') {
                self.mode = 'cancel';
            }
            self.allow_scrap = (!(
                ((picking_type_code !== 'incoming') && (['confirmed', 'cancel', 'progress', 'planned'].indexOf(production_state) !== -1))
                || ((picking_type_code === 'incoming') && (production_state !== 'done'))
            ))

            if (this.quantity_not_available) {
                self.do_notify(_t("Report"), _t("There are movements with no available quantities in this production. Products with no available quantity won't show up."));
            }
        });
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _getLines: function (state) {
        return state.move_raw_ids;
    },

    /**
     * @override
     */
    _lot_name_used: function (product, lot_name) {
        var lines = this._getLines(this.currentState);
        for (var i = 0; i < lines.length; i++) {
            var line = lines[i];
            if (line.qty_done !== 0 && line.product_id.id === product.id &&
                (line.lot_name && line.lot_name === lot_name)) {
                return true;
            }
        }
        return false;
    },

    /**
     * @override
     */
    _getPageFields: function () {
        return [
            ['ok_tech', 'ok_tech'],
            ['availability', 'availability'],
            ['is_locked', 'is_locked'],
            ['state', 'state'],
            ['routing_id', 'routing_id'],
            ['check_to_done', 'check_to_done'],
            ['all_wo_done', 'all_wo_done'],
            ['company_id', 'company_id'],
            ['location_id', 'location_id.id'],
            ['location_name', 'location_id.display_name'],
            ['location_dest_id', 'location_dest_id.id'],
            ['location_dest_name', 'location_dest_id.display_name'],
        ];
    },

    /**
     * @override
     */
    _getWriteableFields: function () {
        return ['product_id.id', 'qty_done', 'location_id.id', 'location_dest_id.id', 'lot_name', 'lot_id.id', 'result_package_id'];
    },

    /**
     * Makes the rpc to `open_produce_product`.
     * This method could open a wizard so it takes care of removing/adding the "barcode_scanned"
     * event listener.
     *
     * @private
     * @returns {Deferred}
     */

    _produce: function () {
        var self = this;
        this.mutex.exec(function () {
            self.context['mode'] = 'ok_tech';
            return self._save().then(function () {
                return self.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'mrp.product.produce',
                    target: 'new',
                    views: [[false, 'form']],
                    context: self.context,
                }, {
                    on_close: function () {
                        self.trigger_up('reload');
                    }
                });
            });
        });
    },

    _mark_as_done: function () {
        var self = this;
        this.mutex.exec(function () {
            return self._save().then(function () {
                return self._rpc({
                    'model': self.actionParams.model,
                    'method': 'button_mark_done',
                    'args': [[self.actionParams.productionId]],
                }).then(function () {
                    self.do_notify(_t("Done"), _t("The production is marked as done"));
                    self.trigger_up('exit');
                });
            });
        });
    },

    _ok_quality: function () {
        var self = this;
        this.mutex.exec(function () {
            self.context['mode'] = 'ok_tech';
            return self._save().then(function () {
                return self.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'quality.wizard',
                    target: 'new',
                    views: [[false, 'form']],
                    context: self.context,
                }, {
                    on_close: function () {
                        self.trigger_up('reload');
                    }
                });
            });
        });
    },

    _button_assign: function () {
        var self = this;
        this.mutex.exec(function () {
            return self._save().then(function () {
                return self._rpc({
                    'model': self.actionParams.model,
                    'method': 'action_assign',
                    'args': [[self.actionParams.productionId]],
                }).then(function () {
                    self.do_notify(_t("Done"), _t("Move lines assigned"));
                    self.trigger_up('reload');
                });
            });
        });
    },

    _create_incident: function () {
        var self = this;
        this.mutex.exec(function () {
            return self._save().then(function () {
                return self.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'model.incident.base',
                    target: 'new',
                    views: [[false, 'form']],
                    context: {'default_model_id': 'mrp.production', 'default_res_id': self.actionParams.productionId},
                }, {
                    on_close: function () {
                        self.trigger_up('reload');
                    }
                });
            });
        });
    },

    /**
     * Makes the rpc to `action_cancel`.
     *
     * @private
     */
    _cancel: function () {
        var self = this;
        this.mutex.exec(function () {
            return self._save().then(function () {
                return self._rpc({
                    'model': self.actionParams.model,
                    'method': 'action_cancel',
                    'args': [[self.actionParams.productionId]],
                }).then(function () {
                    self.do_notify(_t("Cancel"), _t("The transfer has been cancelled"));
                    self.trigger_up('exit');
                });
            });
        });
    },

    /**
     * Makes the rpc to `button_scrap`.
     * This method opens a wizard so it takes care of removing/adding the "barcode_scanned" event
     * listener.
     *
     * @private
     */
    _scrap: function () {
        var self = this;
        this.mutex.exec(function () {
            return self._save().then(function () {
                return self._rpc({
                    'model': 'stock.picking',
                    'method': 'button_scrap',
                    'args': [[self.actionParams.productionId]],
                }).then(function(res) {
                    var exitCallback = function () {
                        core.bus.on('barcode_scanned', self, self._onBarcodeScannedHandler);
                    };
                    var options = {
                        on_close: exitCallback,
                    };
                    core.bus.off('barcode_scanned', self, self._onBarcodeScannedHandler);
                    return self.do_action(res, options);
                });
            });
        });
    },

    /**
     * @override
     */
    _applyChanges: function (changes) {
        var formattedCommands = [];
        var cmd = [];
        for (var i in changes) {
            var line = changes[i];
            if (line.id) {
                // Line needs to be updated
                cmd = [1, line.id, {
                    'qty_done' : line.qty_done,
                    'location_id': line.location_id.id,
                    'location_dest_id': line.location_dest_id.id,
                    'lot_id': line.lot_id && line.lot_id[0],
                    'lot_name': line.lot_name,
                    'package_id': line.package_id ? line.package_id[0] : false,
                    'result_package_id': line.result_package_id ? line.result_package_id[0] : false,
                }];
                formattedCommands.push(cmd);
            } else {
                // Line needs to be created
                cmd = [0, 0, {
                    'picking_id': line.picking_id,
                    'product_id':  line.product_id.id,
                    'product_uom_id': line.product_uom_id[0],
                    'qty_done': line.qty_done,
                    'location_id': line.location_id.id,
                    'location_dest_id': line.location_dest_id.id,
                    'lot_name': line.lot_name,
                    'lot_id': line.lot_id && line.lot_id[0],
                    'state': 'assigned',
                    'package_id': line.package_id ? line.package_id[0] : false,
                    'result_package_id': line.result_package_id ? line.result_package_id[0] : false,
                    'dummy_id': line.virtual_id,
                }];
                formattedCommands.push(cmd);
            }
        }
        if (formattedCommands.length > 0){
            var params = {
                'mode': 'write',
                'model_name': this.actionParams.model,
                'record_id': this.currentState.id,
                'write_vals': formattedCommands,
                'write_field': 'active_move_line_ids',
            };
            return this._rpc({
                'route': '/stock_barcode/get_set_barcode_view_state',
                'params': params,
            });
        } else {
            return $.Deferred().reject();
        }
    },

    /**
     * @override
     */
    _showInformation: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            if (self.formWidget) {
                self.formWidget.destroy();
            }
            self.linesWidget.destroy();
            self.ViewsWidget = new ViewsWidget(
                self,
                'mrp.production',
                'custom_stock_barcode.mrp_production_barcode',
                {},
                {currentId: self.currentState.id},
                'readonly'
            );
            self.ViewsWidget.appendTo(self.$el);
        });
    },

    _print_label: function () {
        var self = this;
        this.mutex.exec(function () {
            return self._save().then(function () {
                return self._rpc({
                    'model': 'mrp.production',
                    'method': 'print_label',
                    'args': [[self.actionParams.productionId]],
                }).then(function(res) {
                    return self.do_action(res);
                });
            });
        });
    },

    _report_finished_product: function () {
        var self = this;
        this.mutex.exec(function () {
            return self._save().then(function () {
                return self.do_action('mrp.action_report_finished_product', {
                    'additional_context': {
                        'active_id': self.actionParams.productionId,
                        'active_ids': [self.actionParams.productionId],
                        'active_model': 'mrp.production',
                    }
                });
            });
        });
    },

    /* There is no recordId because there is no productionId. */
    /* So if the model is mrp.production we need to set it.  */
    _save: function (params) {
        params = params || {};
        var self = this;

        // keep a reference to the currentGroup
        var currentPage = this.pages[this.currentPageIndex];
        if (! currentPage) {
            currentPage = {};
        }
        var currentLocationId = currentPage.location_id;
        var currentLocationDestId = currentPage.location_dest_id;


        // make a write with the current changes
        var recordId = this.actionParams.pickingId || this.actionParams.inventoryId || this.actionParams.productionId;
        var applyChangesDef =  this._applyChanges(this._compareStates()).then(function (state) {
            // Fixup virtual ids in `self.scanned_lines`
            var virtual_ids_to_fixup = _.filter(self._getLines(state[0]), function (line) {
                return line.dummy_id;
            });
            _.each(virtual_ids_to_fixup, function (line) {
                if (self.scannedLines.indexOf(line.dummy_id) !== -1) {
                    self.scannedLines = _.without(self.scannedLines, line.dummy_id);
                    self.scannedLines.push(line.id);
                }
            });

            return self._getState(recordId, state);
        }, function (error) {
            // on server error, let error be displayed and do nothing
            if (error !== undefined) {
                return $.Deferred().reject();
            }
            if (params.forceReload) {
                return self._getState(recordId);
            } else {
                return $.when();
            }
        });

        return applyChangesDef.then(function () {
            self.pages = self._makePages();

            var newPageIndex = _.findIndex(self.pages, function (page) {
                return page.location_id === (params.new_location_id || currentLocationId) &&
                    (self.actionParams.model === 'stock.inventory' ||
                    page.location_dest_id === (params.new_location_dest_id || currentLocationDestId));
            }) || 0;
            if (newPageIndex === -1) {
                newPageIndex = 0;
            }
            self.currentPageIndex = newPageIndex;
        });
    },

    _onEditLine: function (ev) {
        ev.stopPropagation();
        this.linesWidgetState = this.linesWidget.getState();
        this.linesWidget.destroy();
        this.headerWidget.toggleDisplayContext('specialized');

        var virtual_id = _.isString(ev.data.id) ? ev.data.id : false;

        var self = this;
        this.mutex.exec(function () {
            return self._save().then(function () {
                var id = ev.data.id;
                if (virtual_id) {
                    var currentPage = self.pages[self.currentPageIndex];
                    var rec = _.find(currentPage.lines, function (line) {
                        return line.dummy_id === virtual_id;
                    });
                    id = rec.id;
                }

                if (self.actionParams.model === 'mrp.production') {
                    self.ViewsWidget = new ViewsWidget(
                        self,
                        'stock.move.line',
                        'stock_barcode.stock_move_line_product_selector',
                        {},
                        {currentId: id}
                    );
                }
                return self.ViewsWidget.appendTo(self.$el);
            });
        });
    },

    _incrementLines: function (params) {
        var line = this._findCandidateLineToIncrement(params);
        var isNewLine = false;
        if (line) {
            line.qty_done += params.product.qty || 1;
        }

        if (params.lot_id) {
            line.lot_id = [params.lot_id];
        }
        if (params.lot_name) {
            line.lot_name = params.lot_name;
        }
        
        return {
            'id': line.id,
            'virtualId': line.virtual_id,
            'lineDescription': line,
            'isNewLine': isNewLine,
        };
    },

    _step_product: function (barcode, linesActions) {
        var self = this;
        this.currentStep = 'product';
        var errorMessage;
        var action;

        var currentPage = this.pages[this.currentPageIndex];
        if (! currentPage) {
            currentPage = {};
        }
        var currentLocationId = currentPage.location_id;
        var currentLocationDestId = currentPage.location_dest_id;

        return this._isProduct(barcode).then(function (product) {
            console.log("product => ", product);
            if (product) {
                this.line_check = self._findCandidateLineToIncrement({
                    product: product,
                    barcode: barcode,
                });
                if (!this.line_check || !this.line_check.id) {
                    var r = confirm(
                        _t(
                            "The scanned product is not in the production, would you like to add it?"
                        )
                    );
                    if (r == false) {
                        errorMessage = _t("Product addition cancelled");
                    } else {
                        self.context['location_id'] = currentLocationId;
                        self.context['location_dest_id'] = currentLocationDestId;
                        self.context['product_id'] = product.id;
                        self.context['product_uom'] = product.uom_id[0];
                        self.context['raw_material_production_id'] = self.actionParams.productionId;
                        console.log("self.context => ", self.context);
                        action = {
                            type: 'ir.actions.act_window',
                            res_model: 'mrp.production.move.wzd',
                            target: 'new',
                            views: [[false, 'form']],
                            context: self.context,
                        }
                    }
                }
            }

            if (action) {
                return self.do_action(action, {
                    on_close: function () {
                        self.trigger_up('reload');
                    }
                });
            }

            if (errorMessage) {
                return $.Deferred().reject(errorMessage);
            }

            if (product.tracking !== 'none') {
                self.currentStep = 'lot';
            }

            var res = self._incrementLines({'product': product, 'barcode': barcode});
            linesActions.push([self.linesWidget.incrementProduct, [res.id || res.virtualId, 1, self.actionParams.model]]);
            self.scannedLines.push(res.id || res.virtualId);           
            return $.when({linesActions: linesActions});
        }, function () {
            var success = function (res) {
                return $.when({linesActions: res.linesActions});
            };
            var fail = function (specializedErrorMessage) {
                self.currentStep = 'product';
                if (specializedErrorMessage){
                    return $.Deferred().reject(specializedErrorMessage);
                }
                if (! self.scannedLines.length) {
                    if (self.groups.group_tracking_lot) {
                        errorMessage = _t("You are expected to scan one or more products or a package available at the picking's location");
                    } else {
                        errorMessage = _t('You are expected to scan one or more products.');
                    }
                    return $.Deferred().reject(errorMessage);
                }

                var destinationLocation = self.locationsByBarcode[barcode];
                if (destinationLocation) {
                    return self._step_destination(barcode, linesActions);
                } else {
                    errorMessage = _t('You are expected to scan more products or a destination location.');
                    return $.Deferred().reject(errorMessage);
                }
            };
            return self._step_lot(barcode, linesActions).then(success, function () {
                return self._step_package(barcode, linesActions).then(success, fail);
            });
        });
    },

    _onBarcodeScanned: function(barcode) {
        var self = this;
        var res = this._super.apply(this, arguments);
        self._save();
        return res;
    },

    _onReload: function (ev) {
        var self = this;
        this._super.apply(this, arguments);
        var recordId = this.actionParams.pickingId || this.actionParams.inventoryId || this.actionParams.productionId;
        self._getState(recordId);
        this.quantity_not_available = self.currentState.quantity_not_available;

        if (this.quantity_not_available) {
            self.do_notify(_t("Report"), _t("There are movements with no available quantities in this production. Products with no available quantity won't show up."));
        }
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Handles the `mark_as_done` OdooEvent. It makes an RPC call
     * to the method 'button_validate' to validate the current picking
     *
     * @private
     * @param {OdooEvent} ev
     */
     _onMarkAsDone: function (ev) {
        ev.stopPropagation();
        this._mark_as_done();
    },

    /**
     * Handles the `ok_quality` OdooEvent. It makes an RPC call
     * to the method 'button_validate' to validate the current picking
     *
     * @private
     * @param {OdooEvent} ev
     */
     _onOkQuality: function (ev) {
        ev.stopPropagation();
        this._ok_quality();
    },

    /**
     * Handles the `button_assign` OdooEvent. It makes an RPC call
     * to the method 'button_assign' to validate the current picking
     *
     * @private
     * @param {OdooEvent} ev
     */
     _onButtonAssign: function (ev) {
        ev.stopPropagation();
        this._button_assign();
    },

    /**
     * Handles the `validate` OdooEvent. It makes an RPC call
     * to the method 'button_validate' to validate the current picking
     *
     * @private
     * @param {OdooEvent} ev
     */
     _onProduce: function (ev) {
        ev.stopPropagation();
        this._produce();
    },

    /**
     * Handles the `cancel` OdooEvent. It makes an RPC call
     * to the method 'action_cancel' to cancel the current picking
     *
     * @private
     * @param {OdooEvent} ev
     */
    _onCancel: function (ev) {
        ev.stopPropagation();
        this._cancel();
    },

    /**
     * Handles the `print_picking` OdooEvent. It makes an RPC call
     * to the method 'do_print_picking'.
     *
     * @private
     * @param {OdooEvent} ev
     */
     _onPrintFinishedLabel: function (ev) {
        ev.stopPropagation();
        this._report_finished_product();
    },

    /**
     * Handles the `print_delivery_slip` OdooEvent. It makes an RPC call
     * to the method 'do_action' on a 'ir.action_window' with the additional context
     * needed
     *
     * @private
     * @param {OdooEvent} ev
     */
     _onPrintProduction: function (ev) {
        ev.stopPropagation();
        this._print_label();
    },

    /**
     * Handles the `scan` OdooEvent. It makes an RPC call
     * to the method 'button_scrap' to scrap a picking.
     *
     * @private
     * @param {OdooEvent} ev
     */
    _onScrap: function (ev) {
        ev.stopPropagation();
        this._scrap();
    },

    /**
     * Handles the `create incident` OdooEvent. It makes an RPC call
     * to the method 'create_incident' to create a pack and link move lines to it.
     *
     * @private
     * @param {OdooEvent} ev
     */
    _onCreateIncident: function (ev) {
        ev.stopPropagation();
        this._create_incident();
    },
});

core.action_registry.add('stock_barcode_production_client_action', ProductionClientAction);

return ProductionClientAction;

});
