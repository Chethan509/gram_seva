/**
 * GRAMA SEVA – Main Client Application JavaScript
 * Handles form validation, conditional school fields, image previews, modals & UI interactions.
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Password Visibility Toggle
  initPasswordToggles();

  // 2. Complaint Category & Dynamic School Fields
  initCategorySelector();

  // 3. Image Upload Dropzone & Live Preview
  initImageUpload();

  // 4. Modal Handlers
  initModals();

  // 5. Auto dismiss alerts after 6 seconds
  initAlertDismissal();
});

/* -------------------------------------------------------------
   1. Password Visibility Toggle
   ------------------------------------------------------------- */
function initPasswordToggles() {
  const toggleBtns = document.querySelectorAll('.password-toggle-btn');
  toggleBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const targetId = this.getAttribute('data-target') || 'password';
      const input = document.getElementById(targetId);
      if (!input) return;

      const icon = this.querySelector('i');
      if (input.type === 'password') {
        input.type = 'text';
        if (icon) {
          icon.classList.remove('fa-eye');
          icon.classList.add('fa-eye-slash');
        }
      } else {
        input.type = 'password';
        if (icon) {
          icon.classList.remove('fa-eye-slash');
          icon.classList.add('fa-eye');
        }
      }
    });
  });
}

/* -------------------------------------------------------------
   2. Dynamic Category Selection & School Infrastructure Fields
   ------------------------------------------------------------- */
const CATEGORY_PROBLEMS = {
  "1": [ // Water Supply
    "Water shortage in locality",
    "Main supply pipeline leaking / burst",
    "Damaged public drinking water tap",
    "Contaminated / dirty water supply",
    "Borewell motor damaged",
    "Overhead tank cleaning required"
  ],
  "2": [ // Roads and Transportation
    "Dangerous potholes on village road",
    "Broken concrete / asphalt road",
    "Muddy unpaved road during rains",
    "Damaged culvert / bridge approach",
    "Missing village road sign boards",
    "Tree branch obstructing village traffic"
  ],
  "3": [ // Streetlights
    "Streetlight not glowing (Dark street)",
    "Damaged or tilted streetlight pole",
    "Exposed electric wires on pole",
    "Solar streetlight battery fault",
    "Timer switch not turning off in morning",
    "New streetlight installation needed"
  ],
  "4": [ // Garbage Collection
    "Uncollected garbage heap on street",
    "Overflowing public waste bin",
    "Open dumping near agricultural fields",
    "Dead animal removal required",
    "Irregular door-to-door waste collection"
  ],
  "5": [ // Drainage and Sanitation
    "Blocked roadside storm drain",
    "Sewage overflowing onto village road",
    "Stagnant water breeding mosquitoes",
    "Broken drain concrete slab / open pit",
    "Foul odor from neglected gutter"
  ],
  "6": [ // Government School Problems (Special)
    "Damaged classrooms or school buildings",
    "Broken or unclean school toilets",
    "Lack of clean drinking water for students",
    "Electricity faults / no fans or lights",
    "Broken desks and benches",
    "Damaged compound walls / stray animal entry",
    "Poor sanitation around school premises",
    "Other school infrastructure problems"
  ],
  "7": [ // Public Health Facilities
    "Sanitation problems in Primary Health Clinic",
    "Damaged clinic building or leaking roof",
    "Drinking water shortage at Health Sub-Center",
    "Medical waste disposal issue",
    "Lack of basic seating for patients"
  ],
  "8": [ // Public Facilities
    "Damaged Community Hall (Samudaya Bhavana)",
    "Broken roof / seating in Village Bus Shelter",
    "Anganwadi center infrastructure defect",
    "Village Library building maintenance",
    "Damaged public playground equipment"
  ],
  "9": [ // Other Problems
    "Stray cattle / animal menace",
    "Encroachment of public village land",
    "Noise pollution from commercial machines",
    "Public nuisance / illegal dumping",
    "Other unlisted civic problem"
  ]
};

function initCategorySelector() {
  const categorySelect = document.getElementById('category_id');
  const problemTypeSelect = document.getElementById('problem_type');
  const schoolFieldsContainer = document.getElementById('school-special-fields');

  if (!categorySelect) return;

  function handleCategoryChange() {
    const selectedCatId = categorySelect.value;

    // 1. Toggle Government School Specific Fields
    // Category 6 corresponds to Government School Problems
    if (schoolFieldsContainer) {
      if (selectedCatId === "6") {
        schoolFieldsContainer.style.display = 'block';
        // Add required attribute dynamically to school fields
        const schoolNameInput = document.getElementById('school_name');
        if (schoolNameInput) schoolNameInput.required = true;
      } else {
        schoolFieldsContainer.style.display = 'none';
        const schoolNameInput = document.getElementById('school_name');
        if (schoolNameInput) schoolNameInput.required = false;
      }
    }

    // 2. Populate Specific Problem Types
    if (problemTypeSelect) {
      problemTypeSelect.innerHTML = '<option value="">-- Select Specific Problem --</option>';
      const problems = CATEGORY_PROBLEMS[selectedCatId] || [
        "General civic defect",
        "Urgent repair needed",
        "Public safety hazard",
        "Other specific problem"
      ];

      problems.forEach(prob => {
        const opt = document.createElement('option');
        opt.value = prob;
        opt.textContent = prob;
        problemTypeSelect.appendChild(opt);
      });
    }
  }

  categorySelect.addEventListener('change', handleCategoryChange);

  // If a category was pre-selected (via query parameter or reload), trigger change immediately
  if (categorySelect.value) {
    handleCategoryChange();
  }
}

/* -------------------------------------------------------------
   3. Image Upload Dropzone & Live Preview
   ------------------------------------------------------------- */
function initImageUpload() {
  const fileInput = document.getElementById('photo');
  const dropzone = document.getElementById('imageDropzone');
  const previewContainer = document.getElementById('imagePreviewContainer');
  const previewImg = document.getElementById('imagePreview');
  const removeBtn = document.getElementById('removeImageBtn');

  if (!fileInput || !dropzone) return;

  // Click on dropzone opens file dialog
  dropzone.addEventListener('click', function (e) {
    if (e.target !== removeBtn && !removeBtn?.contains(e.target)) {
      fileInput.click();
    }
  });

  // Drag and drop handlers
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, function (e) {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, function (e) {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    }, false);
  });

  dropzone.addEventListener('drop', function (e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      fileInput.files = files;
      showPreview(files[0]);
    }
  });

  fileInput.addEventListener('change', function () {
    if (this.files && this.files[0]) {
      showPreview(this.files[0]);
    }
  });

  function showPreview(file) {
    // Validate file type & size (max 10MB)
    const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    if (!validTypes.includes(file.type)) {
      alert("Please upload a valid image file (JPG, PNG, WEBP).");
      fileInput.value = '';
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      alert("Image file size exceeds 10MB. Please select a smaller photo.");
      fileInput.value = '';
      return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
      if (previewImg) previewImg.src = e.target.result;
      if (previewContainer) previewContainer.style.display = 'block';
      const promptEl = dropzone.querySelector('.upload-prompt');
      if (promptEl) promptEl.style.display = 'none';
    };
    reader.readAsDataURL(file);
  }

  if (removeBtn) {
    removeBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      fileInput.value = '';
      if (previewContainer) previewContainer.style.display = 'none';
      const promptEl = dropzone.querySelector('.upload-prompt');
      if (promptEl) promptEl.style.display = 'block';
    });
  }
}

/* -------------------------------------------------------------
   4. Modal Dialog Handlers
   ------------------------------------------------------------- */
function initModals() {
  const closeButtons = document.querySelectorAll('[data-dismiss="modal"]');
  closeButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      const modal = this.closest('.civic-modal-backdrop');
      if (modal) modal.classList.remove('show');
    });
  });

  // Close when clicking on backdrop
  const modals = document.querySelectorAll('.civic-modal-backdrop');
  modals.forEach(modal => {
    modal.addEventListener('click', function (e) {
      if (e.target === this) {
        this.classList.remove('show');
      }
    });
  });

  // Close on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      modals.forEach(modal => modal.classList.remove('show'));
    }
  });
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('show');
  }
}

/* -------------------------------------------------------------
   5. Auto dismiss flash alerts
   ------------------------------------------------------------- */
function initAlertDismissal() {
  const alerts = document.querySelectorAll('.civic-alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      setTimeout(() => alert.remove(), 500);
    }, 6000);
  });
}
