<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && backlogItem" class="modal-overlay" @click="close">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">{{ mode === 'view' ? 'Purchase Order Details' : 'Create Purchase Order' }}</h3>
            <button class="close-button" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <form v-if="mode === 'create'" class="modal-form" @submit.prevent="submit">
            <div class="modal-body">
              <div class="item-summary">
                <div class="info-item">
                  <div class="info-label">Order ID</div>
                  <div class="info-value order-id">{{ backlogItem.order_id }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Item SKU</div>
                  <div class="info-value sku">{{ backlogItem.item_sku }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Item</div>
                  <div class="info-value">{{ translateProductName(backlogItem.item_name) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Shortage</div>
                  <div class="info-value">{{ shortage }} units</div>
                </div>
              </div>

              <div class="form-grid">
                <div class="form-field full">
                  <label class="info-label" for="po-supplier">Supplier Name</label>
                  <input id="po-supplier" v-model="form.supplier_name" class="form-input" type="text" required />
                </div>
                <div class="form-field">
                  <label class="info-label" for="po-quantity">Quantity</label>
                  <input id="po-quantity" v-model.number="form.quantity" class="form-input" type="number" min="1" step="1" required />
                </div>
                <div class="form-field">
                  <label class="info-label" for="po-cost">Unit Cost (USD)</label>
                  <input id="po-cost" v-model.number="form.unit_cost" class="form-input" type="number" min="0.01" step="0.01" required />
                </div>
                <div class="form-field full">
                  <label class="info-label" for="po-date">Expected Delivery Date</label>
                  <input id="po-date" v-model="form.expected_delivery_date" class="form-input" type="date" required />
                </div>
                <div class="form-field full">
                  <label class="info-label" for="po-notes">Notes (optional)</label>
                  <textarea id="po-notes" v-model="form.notes" class="form-input" rows="3"></textarea>
                </div>
              </div>

              <div class="total-row">
                <span class="info-label">Total Cost</span>
                <span class="total-value">{{ formatMoney(totalCost) }}</span>
              </div>

              <div v-if="error" class="error-message" role="alert">{{ error }}</div>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="close">Cancel</button>
              <button type="submit" class="btn-primary" :disabled="saving">
                {{ saving ? 'Saving...' : 'Create Purchase Order' }}
              </button>
            </div>
          </form>

          <template v-else>
            <div class="modal-body">
              <div v-if="loading" class="state-message">Loading purchase order...</div>
              <div v-else-if="error" class="error-message" role="alert">{{ error }}</div>
              <div v-else-if="purchaseOrder" class="info-grid">
                <div class="info-item">
                  <div class="info-label">PO Number</div>
                  <div class="info-value sku">{{ purchaseOrder.id }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Status</div>
                  <div class="info-value">{{ purchaseOrder.status }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Supplier</div>
                  <div class="info-value">{{ purchaseOrder.supplier_name }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Item</div>
                  <div class="info-value">{{ translateProductName(backlogItem.item_name) }} ({{ backlogItem.item_sku }})</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Quantity</div>
                  <div class="info-value">{{ purchaseOrder.quantity }} units</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Unit Cost</div>
                  <div class="info-value">{{ formatMoney(purchaseOrder.unit_cost) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Total Cost</div>
                  <div class="info-value">{{ formatMoney(purchaseOrder.quantity * purchaseOrder.unit_cost) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Expected Delivery</div>
                  <div class="info-value">{{ formatDate(purchaseOrder.expected_delivery_date) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Created</div>
                  <div class="info-value">{{ formatDate(purchaseOrder.created_date) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Notes</div>
                  <div class="info-value">{{ purchaseOrder.notes || 'N/A' }}</div>
                </div>
              </div>
            </div>

            <div class="modal-footer">
              <button class="btn-secondary" @click="close">Close</button>
            </div>
          </template>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrencyWithDecimals } from '../utils/currency'

const { translateProductName } = useI18n()

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  backlogItem: {
    type: Object,
    default: null
  },
  mode: {
    type: String,
    default: 'create',
    validator: (value) => ['create', 'view'].includes(value)
  }
})

const emit = defineEmits(['close', 'po-created'])

const form = reactive({
  supplier_name: '',
  quantity: 1,
  unit_cost: null,
  expected_delivery_date: '',
  notes: ''
})
const saving = ref(false)
const loading = ref(false)
const error = ref(null)
const purchaseOrder = ref(null)

const shortage = computed(() => {
  if (!props.backlogItem) return 0
  return props.backlogItem.quantity_needed - props.backlogItem.quantity_available
})

const totalCost = computed(() => (Number(form.quantity) || 0) * (Number(form.unit_cost) || 0))

const close = () => {
  emit('close')
}

const resetForm = () => {
  form.supplier_name = ''
  form.quantity = Math.max(shortage.value, 1)
  form.unit_cost = null
  form.expected_delivery_date = ''
  form.notes = ''
}

const loadPurchaseOrder = async () => {
  if (props.backlogItem.purchase_order) {
    purchaseOrder.value = props.backlogItem.purchase_order
    return
  }
  loading.value = true
  try {
    purchaseOrder.value = await api.getPurchaseOrderByBacklogItem(props.backlogItem.id)
  } catch (err) {
    error.value = 'Failed to load purchase order'
    console.error('Purchase order load error:', err)
  } finally {
    loading.value = false
  }
}

const submit = async () => {
  if (saving.value) return
  saving.value = true
  error.value = null
  try {
    const po = await api.createPurchaseOrder({
      backlog_item_id: props.backlogItem.id,
      supplier_name: form.supplier_name.trim(),
      quantity: form.quantity,
      unit_cost: form.unit_cost,
      expected_delivery_date: form.expected_delivery_date,
      notes: form.notes.trim() || null
    })
    emit('po-created', po)
  } catch (err) {
    // Backend uses 409 for an existing PO and 404 for an unknown backlog item
    const status = err.response?.status
    if (status === 409) error.value = 'A purchase order already exists for this item.'
    else if (status === 404) error.value = 'Backlog item not found.'
    else error.value = 'Failed to create purchase order. Please try again.'
    console.error('Purchase order create error:', err)
  } finally {
    saving.value = false
  }
}

// Reset state each time the modal opens
watch(() => props.isOpen, (open) => {
  if (!open || !props.backlogItem) return
  error.value = null
  purchaseOrder.value = null
  saving.value = false
  if (props.mode === 'view') {
    loadPurchaseOrder()
  } else {
    resetForm()
  }
})

// Amounts are entered in USD, so always display USD regardless of the UI currency
const formatMoney = (amount) => formatCurrencyWithDecimals(amount, 'USD', 2)

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  // Date-only strings parse as UTC and can shift a day; anchor to local midnight
  const date = new Date(/^\d{4}-\d{2}-\d{2}$/.test(dateString) ? `${dateString}T00:00:00` : dateString)
  if (isNaN(date.getTime())) return 'N/A'
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  padding: var(--space-4);
}

.modal-container {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  /* Never wider than the viewport minus the overlay gutters (390px screens) */
  max-width: min(700px, calc(100vw - 2rem));
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: var(--space-2);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition: background var(--transition), color var(--transition);
}

.close-button:hover {
  background: var(--color-surface-muted);
  color: var(--color-text);
}

.close-button:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.modal-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: var(--space-6);
}

.modal-footer {
  padding: var(--space-6);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}

.btn-secondary {
  padding: var(--space-2) var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  font-weight: 500;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: background var(--transition), border-color var(--transition);
  font-family: inherit;
}

.btn-secondary:hover {
  background: var(--color-surface-muted);
}

.btn-secondary:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.modal-form {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.item-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(160px, 100%), 1fr));
  gap: var(--space-4);
  padding: var(--space-5);
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-6);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  min-width: 0;
}

.form-field.full {
  grid-column: 1 / -1;
}

.form-input {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-family: inherit;
  color: var(--color-text);
  background: var(--color-surface);
}

.form-input:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 1px;
}

textarea.form-input {
  resize: vertical;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--space-4);
  padding: var(--space-4) var(--space-5);
  background: var(--color-surface-muted);
  border-radius: var(--radius-md);
}

.total-value {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--color-text);
  font-variant-numeric: tabular-nums;
}

.error-message {
  margin-top: var(--space-4);
  padding: var(--space-3) var(--space-4);
  background: var(--color-danger-soft);
  border: 1px solid var(--color-danger-soft);
  border-radius: var(--radius-md);
  color: var(--color-danger);
  font-size: var(--text-sm);
}

.state-message {
  padding: var(--space-8) 0;
  text-align: center;
  color: var(--color-text-muted);
}

.btn-primary {
  padding: var(--space-2) var(--space-4);
  background: var(--color-accent);
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-md);
  font-weight: 500;
  font-size: var(--text-sm);
  color: #ffffff;
  cursor: pointer;
  font-family: inherit;
  transition: opacity var(--transition);
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

@media (max-width: 520px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(200px, 100%), 1fr));
  gap: var(--space-6);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.info-label {
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}

.info-value {
  font-size: var(--text-base);
  color: var(--color-text);
  font-weight: 500;
}

.info-value.order-id,
.info-value.sku {
  font-family: 'Monaco', 'Courier New', monospace;
  color: var(--color-accent);
}

/* Modal transition animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
