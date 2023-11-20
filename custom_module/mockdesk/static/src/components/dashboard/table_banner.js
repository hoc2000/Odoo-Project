/** @odoo-module */

import { registry } from "@web/core/registry"
import { kanbanView } from "@web/views/kanban/kanban_view"
import { KanbanController } from "@web/views/kanban/kanban_controller"

class HelpdeskKanBanController extends KanbanController {
    setup() {
        super.setup()
        console.log("this is banner table")
    }
}

export const helpDeskKanbanView = {
    //Lấy tất cả attrs của listView
    ...kanbanView,
    //Thay thế controller bằng controller trên
    Controller: HelpdeskKanBanController,
}

HelpdeskKanBanController.template = "owl.HelpdeskTableKanbanView"

registry.category("views").add("helpdesk_table_kanban_view", helpDeskKanbanView);