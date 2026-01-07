package com.ecommerce.controller;

import com.ecommerce.dto.UserDTO;
import com.ecommerce.entity.User;
import com.ecommerce.exception.ResourceNotFoundException;
import com.ecommerce.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/users")
@Tag(name = "User Management", description = "APIs for managing users")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping
    @Operation(summary = "Get all users", description = "Retrieve a paginated list of all users")
    public ResponseEntity<ApiResponse<Page<UserDTO>>> getAllUsers(
            @Parameter(description = "Page number (0-indexed)") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Number of items per page") @RequestParam(defaultValue = "10") int size,
            @Parameter(description = "Sort by field") @RequestParam(defaultValue = "id") String sortBy,
            @Parameter(description = "Sort direction (asc/desc)") @RequestParam(defaultValue = "asc") String sortDir) {
        
        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        
        Page<UserDTO> users = userService.getAllUsers(pageable);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Users retrieved successfully", users));
    }
    
    @GetMapping("/{id}")
    @Operation(summary = "Get user by ID", description = "Retrieve a user by their unique ID")
    public ResponseEntity<ApiResponse<UserDTO>> getUserById(@PathVariable Long id) {
        Optional<UserDTO> user = userService.getUserById(id);
        if (user.isEmpty()) {
            throw new ResourceNotFoundException("User", id);
        }
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "User retrieved successfully", user.get()));
    }
    
    @GetMapping("/username/{username}")
    @Operation(summary = "Get user by username", description = "Retrieve a user by their username")
    public ResponseEntity<ApiResponse<UserDTO>> getUserByUsername(@PathVariable String username) {
        Optional<UserDTO> user = userService.getUserByUsername(username);
        if (user.isEmpty()) {
            throw new ResourceNotFoundException("User", "username", username);
        }
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "User retrieved successfully", user.get()));
    }
    
    @GetMapping("/email/{email}")
    @Operation(summary = "Get user by email", description = "Retrieve a user by their email")
    public ResponseEntity<ApiResponse<UserDTO>> getUserByEmail(@PathVariable String email) {
        Optional<UserDTO> user = userService.getUserByEmail(email);
        if (user.isEmpty()) {
            throw new ResourceNotFoundException("User", "email", email);
        }
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "User retrieved successfully", user.get()));
    }
    
    @PostMapping
    @Operation(summary = "Create a new user", description = "Create a new user in the system")
    public ResponseEntity<ApiResponse<UserDTO>> createUser(@Valid @RequestBody UserDTO userDTO) {
        UserDTO createdUser = userService.createUser(userDTO);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(new ApiResponse<>(HttpStatus.CREATED.value(), "User created successfully", createdUser));
    }
    
    @PutMapping("/{id}")
    @Operation(summary = "Update user", description = "Update an existing user by ID")
    public ResponseEntity<ApiResponse<UserDTO>> updateUser(@PathVariable Long id, @Valid @RequestBody UserDTO userDTO) {
        Optional<UserDTO> existingUser = userService.getUserById(id);
        if (existingUser.isEmpty()) {
            throw new ResourceNotFoundException("User", id);
        }
        UserDTO updatedUser = userService.updateUser(id, userDTO);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "User updated successfully", updatedUser));
    }
    
    @DeleteMapping("/{id}")
    @Operation(summary = "Delete user", description = "Delete a user by ID")
    public ResponseEntity<ApiResponse<Void>> deleteUser(@PathVariable Long id) {
        Optional<UserDTO> user = userService.getUserById(id);
        if (user.isEmpty()) {
            throw new ResourceNotFoundException("User", id);
        }
        userService.deleteUser(id);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "User deleted successfully", null));
    }
    
    @GetMapping("/role/{role}")
    @Operation(summary = "Get users by role", description = "Retrieve users by their role")
    public ResponseEntity<ApiResponse<List<UserDTO>>> getUsersByRole(@PathVariable User.Role role) {
        List<UserDTO> users = userService.getUsersByRole(role);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Users retrieved successfully", users));
    }
    
    @GetMapping("/enabled/{enabled}")
    @Operation(summary = "Get users by enabled status", description = "Retrieve users by their enabled status")
    public ResponseEntity<ApiResponse<List<UserDTO>>> getEnabledUsers(@PathVariable boolean enabled) {
        List<UserDTO> users = userService.getEnabledUsers(enabled);
        return ResponseEntity.ok(new ApiResponse<>(HttpStatus.OK.value(), "Users retrieved successfully", users));
    }
}